from ast import Lambda
from random import uniform
import subprocess
import time
from pandas import read_excel
from rusty_results import Ok, Err, Result # type: ignore
from iw_interpret import Cell
# from ui import PrintCellSimple
from enums import Data, WifiInterface
import pyperf
import cProfile
import re

VU_IF = WifiInterface.WLP1S0
AP_DF = read_excel(Data.AP_MAC)
    
def APsFromScanList(ssid, frequencies, interface = VU_IF) -> Result[list[Cell], str]:
    
    match Scan(interface, frequencies):
        case Ok(cells):
            result = []
            
            for cell in cells:
                if cell.ssid == ssid:
                    result.append(cell)
                    
            if len(result):
                # print(result)
                return Ok(result)

            return Err(f"Connection with SSID {ssid} not found")
        
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
        return Err(str(e))
    
def FilterAPs(cells) -> tuple[list[Cell], list[Cell]]:
    excel_aps = []
    other_aps = []
    
    for cell in cells:
        address = cell.address
        in_excel = AP_DF['Base Radio MAC Address'].eq(address).any()
        
        if in_excel:
            query = "`Base Radio MAC Address` == @address"
            name = AP_DF.query(query)["AP Name"].item()
            # print(f"Found! {name}")
            cell.name = name
            excel_aps.append(cell)
            # excel_aps_names.append(name)
        else:
            other_aps.append(cell)
            
        # PrintCellSimple(cell, cell_index, in_excel)    
    
    return excel_aps, other_aps
        
def FindAPs(ssid, frequencies, interface, min_aps = -1) -> tuple[list[Cell], list[Cell]]:
   
    cell_list = APsFromScanList(ssid, frequencies, interface)
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
        
        cell_list = APsFromScanList(ssid, frequencies, interface)
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
    # frequency = int(input("Which frequency are we scanning?\n2412, 2437, 2462\n5180, 5200, 5220, 5240, 5260, 5280, 5300, 5320, 5500, 5520, 5560, 5580?\n"))
    frequency = 5500
    # runner = pyperf.Runner()
    
    def func():
        min_ms_ago, max_ms_ago, all_results, good_amounts = ([],[],[],[])
        sleep_time = 0.01

        for i in range(1000):
            
            trigger()
            min_now, max_now, results = dump()
            min_ms_ago.append(min_now)
            max_ms_ago.append(max_now)
            all_results.append(results)
            time.sleep(sleep_time)
        
        min_ms_ago = sorted(min_ms_ago)
        max_ms_ago = sorted(max_ms_ago, reverse=True)
        print(f"Min: {min_ms_ago}")
        print(f"Max: {max_ms_ago}")
        
        for i, result in enumerate(all_results):
            print(f"Result {i}: {result}")
            good_result_amount = len(list(filter(lambda x: x>=-67, result)))
            good_amounts.append(good_result_amount)
        print(good_amounts)
        print({x: good_amounts.count(x) for x in set(good_amounts)})


    def trigger():
        subprocess.run(
            ['sudo', '/sbin/iw', 'dev', VU_IF, 'scan', 'trigger', 'flush']
            )
        
    def dump():
        
        try:
            
            iwlist_scan = subprocess.run(
                ['sudo', '/sbin/iw', 'dev', VU_IF, 'scan', 'dump'],
                        capture_output=True).stdout
            # print(str(iwlist_scan))

            # 0 = BSS, 1 = frequency, 2 = signal, 3 = last seen, 4 = SSID
            pattern = r"(?:BSS )((?:[\da-z]{2}:){5}[\da-z]{2})(?:.*?freq: )(\d*)(?:.*?signal: )(-\d+\.\d*)(?:.*?last seen: )(\d+)(?:.*?SSID: )([^\\]+)"
            readable_scan = re.findall(pattern, str(iwlist_scan))
            # print(readable_scan)
            ssid_specific = filter(lambda scan_params: str(scan_params[4]).endswith("VU-Campusnet"), readable_scan)
            chronological_scan = sorted(ssid_specific, key=lambda scan_params: int(scan_params[3]))
            OLDEST_IN_MS = 6000
            fresh_results = list(filter(lambda scan_params: int(scan_params[3].split()[0]) <= OLDEST_IN_MS, chronological_scan))

            for result in fresh_results:
                print(f"MAC <{result[0]}> (@freq: {result[1]} MHz) = {result[2]} dBm")
                print(f"\tlast seen {result[3]} ms ago")

            minimum = int(chronological_scan[0][2].split()[0])
            maximum = int(chronological_scan[-1][2].split()[0])
            signal_strengths = map(lambda scan_params: int(scan_params[2].split(".")[0]), fresh_results)
            
            print("scan dump succeeded!")
            return (minimum, maximum, sorted(list(signal_strengths)))
        
        except:
            
            print("scan dump failed!")
            time.sleep(0.05)
            return (9999, 0, 0)

    # runner.bench_func('Cell.all', func)
    cProfile.run('func()')  

    # runner.timeit(name = "scan actively on one frequency",
    #               stmt = "result = r",
    #               setup = f"r = list(Cell.all({VU_IF}, {[freq]}))")
    # Cell.all(VU_IF, [freq])