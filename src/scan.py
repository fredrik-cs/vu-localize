from datetime import datetime
import logging
from random import uniform
import subprocess
import time
from pandas import read_excel
from rusty_results import Ok, Err, Result # type: ignore
from src.iw_interpret import Cell
# from ui import PrintCellSimple
from src.enums import Data, WifiInterface, SSIDs, Band
import pyperf
import cProfile
import re
from src.ui import PrintCellSimple

VU_IF = WifiInterface.WLP1S0
AP_DF = read_excel(Data.AP_MAC)
    
def APsFromScanList(ssids, frequencies, interface = VU_IF) -> Result[list[Cell], str]:
    
    match Scan(interface, frequencies):
        case Ok(cells):
            result = []
            
            for cell in cells:
                if cell.ssid in ssids:
                    result.append(cell)
                    
            if len(result):
                # print(result)
                return Ok(result)

            return Err(f"Connection with SSIDs {ssids} not found")
        
        case Err(e):
            return Err(e)

# def FindAtleastMinScans(ssid, frequencies, min = 3) -> Result[list[Cell], None]:
#     result = []
#     addresses = []
    
#     while len(result) < min:
#         match FindFromScanList(ssid, frequencies):
#             case Ok(cells):
#                 for cell in cells:
#                     if cell.address not in addresses:
#                         addresses.append(cell.address)
#                         result.append(cell)
#             case Err(_):
#                 pass
    
#     return Ok(result)
            

def Scan(interface = VU_IF, frequencies = []) -> Result[list[Cell], str]:
    cell_list = []
    
    try:
        cell_map = Cell.all(interface, frequencies)
        # print(cell_map)
        
        for cell in cell_map:
            cell.address = cell.address.lower()
            cell_list.append(cell)       
        
        # print(cell_list)
        return Ok(cell_list)
    
    except Exception as e:
        #TODO: error handling
        print(e)
        return Err(str(e))
    
def FilterAPs(cells: list[Cell]) -> tuple[list[Cell], list[Cell]]:
    excel_aps = []
    other_aps = []
    cell_index = 0
    
    for cell in cells:
        address = cell.address[:-1]+"0"
        in_excel = AP_DF['Base Radio MAC Address'].eq(address).any()
        
        if in_excel:
            query = "`Base Radio MAC Address` == @address"
            name = AP_DF.query(query)["AP Name"].item()
            print(f"Found! {name}")
            cell.name = name
            excel_aps.append(cell)
            # excel_aps_names.append(name)
        else:
            other_aps.append(cell)
            
        cell_index += 1    
        PrintCellSimple(cell, cell_index, in_excel)    
    
    return excel_aps, other_aps
        
def FindAPs(ssids, frequencies, interface, min_aps = -1) -> tuple[list[Cell], list[Cell]]:
   
    cell_list = APsFromScanList(ssids, frequencies, interface)
    # cell_list = FindAtleastMinScans(ssid, interface, 3)
    # cell_list = Scan(interface)
    excel_aps = []
    other_aps = []
    
    match cell_list:
        
        case Err(_e):
            #TODO: error handling
            print(f"ERROR: {_e}")
            return [], []
        
        case Ok(cells):
            
            print('#' * 10)
            excel_aps, other_aps = FilterAPs(cells)
            print(f"Found {len(excel_aps)} (+{len(other_aps)} = {len(excel_aps) + len(other_aps)}):")
            print(excel_aps)
            
    while len(excel_aps) < min_aps:
        duration = uniform(0.1, 0.5)
        time.sleep(duration)
        
        cell_list = APsFromScanList(ssids, frequencies, interface)
        match cell_list:
            case Err(e):
                pass
            
            case Ok(cells):
                w_excel_aps, w_other_aps = FilterAPs(cells)
                for ap in w_excel_aps:
                    if ap.name not in map(lambda xap: xap.name, excel_aps):
                        excel_aps.append(ap)
                        print(f"Added: {ap}")
                for ap in w_other_aps:
                    if ap.address not in map(lambda oap: oap.address, other_aps):
                        other_aps.append(ap)
                
    print(f"Found {len(excel_aps)} (+{len(other_aps)} = {len(excel_aps) + len(other_aps)}):")
    print(excel_aps)

    return excel_aps, other_aps

if __name__ == "__main__":
    
    pass

    

    # def scan_and_log(band, ssid, logger: logging.Logger):
    #     min_ms_ago, max_ms_ago, signals_per_dump, good_amounts = ([],[],[],[])
    #     mac_signal_dict = {}
    #     freq_signal_dict = {}
    #     ITERATION_DELAY = 0.01
    #     ITERATIONS = 192 # 1920 - 2000 

    #     for i in range(ITERATIONS):
            
    #         Cell.trigger_scan(band)
    #         dump = Cell._dump()
    #         min_now, max_now, results = process_dump(ssid, dump)

    #         min_ms_ago.append(min_now)
    #         max_ms_ago.append(max_now)

    #         signals = [result[2] for result in results]
    #         print(signals)
    #         signals_per_dump.append(signals)

    #         for result in results:
    #             if result[0] not in mac_signal_dict:
    #                 mac_signal_dict[result[0]] = [{result[2]: 1}]
    #             elif list(mac_signal_dict[result[0]][-1].keys()) != [result[2]]:
    #                 mac_signal_dict[result[0]].append({result[2]: 1})
    #             else:
    #                 mac_signal_dict[result[0]][-1][result[2]] += 1
                    
    #             if result[1] not in freq_signal_dict:
    #                 freq_signal_dict[result[1]] = {result[2]: 1}
    #             elif result[2] not in freq_signal_dict[result[1]]:
    #                 freq_signal_dict[result[1]][result[2]] = 1
    #             else:
    #                freq_signal_dict[result[1]][result[2]] += 1 
    #         freq_signal_dict = {k: v for k, v in sorted(freq_signal_dict.items(), key=lambda item: int(item[0]))}

    #         time.sleep(ITERATION_DELAY)
        
    #     min_ms_ago = sorted(min_ms_ago)
    #     max_ms_ago = sorted(max_ms_ago, reverse=True)
    #     print(f"Min: {min_ms_ago}")
    #     print(f"Max: {max_ms_ago}")
        
    #     previous_new_result = []
    #     MIN_SIGNAL_STRENGTH = -67
    #     for i, signals in enumerate(signals_per_dump):
    #         if signals != previous_new_result:
    #             print(f"Result {i}: {signals}")
    #             previous_new_result = signals
    #         good_signals_amount = len(list(filter(lambda signal: signal>=MIN_SIGNAL_STRENGTH, signals)))
    #         good_amounts.append(good_signals_amount)
    #     # print(good_amounts)
    #     print({x: good_amounts.count(x) for x in set(good_amounts)})

    #     # Variance when standing still measure
    #     prev_strength = 0
        
    #     for mac in mac_signal_dict:

    #         summary = ""
    #         distance_moved = 0
    #         distance_traveled = 0
    #         white_space_counter = 0
    #         log_line = "\t"
    #         max_strength = -100
    #         min_strength = 0

    #         # received signals, in order:
    #         logger.info(f"\nfrom MAC<{mac}>")
            
    #         for signal in mac_signal_dict[mac]:

    #             strength = list(signal.keys())[0] 
    #             count = signal[strength]
    #             log_line += f"{count} at {strength} dBm, "

    #             white_space_counter += 1
                
    #             if white_space_counter >= 5:
    #                 logger.debug(log_line)
    #                 log_line = "\t"
    #                 white_space_counter = 0

    #             if prev_strength != 0:
    #                 difference = strength - prev_strength
    #                 summary += f"+{difference} "
    #                 distance_moved += (difference)
    #                 distance_traveled += abs(difference)

    #             max_strength = max(max_strength, strength)
    #             min_strength = min(min_strength, strength)
    #             prev_strength = strength 

    #         if log_line != "\t":
    #             logger.debug(f"{log_line}")
            
    #         logger.debug(f"Changes: ( {summary})")
    #         logger.debug(f"= {distance_moved}")
    #         logger.info(f"margins = {abs(min_strength)}-{abs(max_strength)} = {max_strength - min_strength} | total = {distance_traveled}")
    #         prev_strength = 0
    #         logger.debug(f"\n{'-' * 90}")
            
    #     # Signal strength per band measure

    #     signals_count = 0
    #     previous_freq = 0
    #     mid_log = ""
    #     end_log = ""
    #     mid_sum = 0
    #     end_sum = 0
    #     mid_count = 0
    #     end_count = 0

    #     logger.info("\n-----2.4GHz band-----")
    #     for freq in freq_signal_dict:

    #         if int(previous_freq) < 3000 and int(freq) > 4000:
    #             logger.info(f"Band total: {signals_count} signals")
    #             if (end_count > 0):
    #                 logger.debug(f"Average Strength on band: ({end_log[:-1]}) / {end_count}")
    #                 logger.info(f"= {end_sum / end_count}") 

    #             end_log = ""
    #             end_count = 0
    #             end_sum = 0
    #             signals_count = 0

    #             logger.info("\n-----5GHz band-----")

    #         logger.info(f"@{freq} MHz")

    #         for signal in freq_signal_dict[freq]:

    #             count = freq_signal_dict[freq][signal]
    #             logger.debug(f"\t{count} signals at {signal} dBM were received")

    #             signals_count += count
    #             mid_log += f" {count}*{signal} +"
    #             mid_count += count
    #             mid_sum += count*signal
            
    #         if (mid_count > 0): 
    #             logger.debug(f"Average Strength on channel: ({mid_log[:-1]}) / {mid_count}")
    #             logger.info(f"= {mid_sum / mid_count}\n")

    #         end_log += mid_log
    #         end_count += mid_count
    #         end_sum += mid_sum
    #         mid_log = ""
    #         mid_count = 0
    #         mid_sum = 0
    #         previous_freq = freq

    #     logger.info(f"Band total: {signals_count} signals")
    #     if (end_count > 0):
    #         logger.debug(f"Average Strength on band: ({end_log[:-1]}) / {end_count}")
    #         logger.info(f" = {end_sum / end_count}\n")
        

    # def trigger(freqs):

    #     if freqs:
    #         frequencies = list(map(lambda x: str(x), freqs))
    #         subprocess.run(
    #             ['sudo', '/sbin/iw', 'dev', VU_IF, 'scan', 'trigger', 'freq', *frequencies, 'flush']
    #             )

    #     else:
    #         subprocess.run(
    #             ['sudo', '/sbin/iw', 'dev', VU_IF, 'scan', 'trigger', 'flush']
    #             )
        
    
        
        

    
