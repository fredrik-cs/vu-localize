from datetime import datetime
import logging
import re
import time

from src.enums import SSIDs
from src.iw_interpret import Cell

def new_logger(name):

        logger = logging.getLogger(name)
        handler = logging.FileHandler("experiments/draftzero/"+name+".log")
        logger.addHandler(handler)

        return logger

def LogBandQualities(band, file_name): 
        ITERATION_DELAY = 0.01
        ITERATIONS = 192 # 1920 - 2000

        loggers = []
        loggers.append(new_logger(file_name+"-camp"))
        loggers.append(new_logger(file_name+"-edu"))
        loggers.append(new_logger(file_name+"-iot"))
        ssids = [SSIDs.VU_CAMPUSNET, SSIDs.EDUROAM, SSIDs.IOTROAM]
        level = logging.INFO

        logging.basicConfig(level=level, format="%(message)s")
        
        for logger, ssid in zip(loggers, ssids):
            #scan_and_log(band, ssid, logger)
            scans = []

            for i in range(ITERATIONS):
                results = debug_scan(band, ssid)
                scans.append(results)

                time.sleep(ITERATION_DELAY)

            log_debug_scan(logger, scans)

def debug_scan(band, ssid):
        try:
            Cell.trigger_scan(band)
            iw_dump = Cell._dump()
            return process_dump(iw_dump, ssid)

        except Exception as e:
            print(e)
            print("scan dump failed!")
            time.sleep(0.05)
            return [None]

def process_dump(scan_dump, ssid):
        
    ts = time.time_ns()

    # 0 = BSS, 1 = frequency, 2 = signal, 3 = last seen, 4 = SSID
    pattern = r"(?:BSS )((?:[\da-z]{2}:){5}[\da-z]{2})(?:.*?freq: )(\d*)(?:.*?signal: )(-\d+)(?:.*?last seen: )(\d+)(?:.*?SSID: )([^\\]+)"
    readable_scan = re.findall(pattern, str(scan_dump))
    # print(readable_scan)
    ssid_specific = filter(lambda scan_params: str(scan_params[4]).endswith(ssid), readable_scan)
    chronological_scan = sorted(ssid_specific, key=lambda scan_params: int(scan_params[3]))
    
    for i, result in enumerate(chronological_scan):
        print(f"MAC <{result[0]}> (@freq: {result[1]} MHz) = {result[2]} dBm")
        print(f"\tlast seen {result[3]} ms ago")
        result = list(result)
        result[3] = ts - float(result[3]) * 1_000_000
        print(f"\tor at timestamp {[result[3]]} ({datetime.fromtimestamp(result[3] / 1e9)})")
        chronological_scan[i] = result
        chronological_scan[i][2] = int(result[2])
    
    print("scan dump succeeded!")
    return (chronological_scan)

def log_debug_scan(logger, results_per_iter):
        signals_per_dump, good_amounts = ([],[])
        mac_signal_dict, freq_signal_dict = ({}, {})
        MIN_SIGNAL_STRENGTH = -67
        # OLDEST_IN_MS = 6000
        # fresh_results = list(filter(lambda scan_params: int(scan_params[3]) <= OLDEST_IN_MS, chronological_scan))

        for results in results_per_iter:

            signals = [result[2] for result in results]
            print(signals)
            signals_per_dump.append(signals)

        results = [result 
                   for results in results_per_iter 
                   for result in results]

        for result in results:
            mac = result[0]
            frequency = result[1]
            signal = result[2]

            # dictionary that holds for every BSD a ledger of signals and how many times they were recorded in order
            if mac not in mac_signal_dict:
                mac_signal_dict[mac] = [{signal: 1}]
            elif list(mac_signal_dict[mac][-1].keys()) != [signal]:
                mac_signal_dict[mac].append({signal: 1})
            else:
                mac_signal_dict[mac][-1][signal] += 1
                
            # dictionary that holds for every channel how many times any given signal strength was recorded
            if frequency not in freq_signal_dict:
                freq_signal_dict[frequency] = {signal: 1}
            elif signal not in freq_signal_dict[frequency]:
                freq_signal_dict[frequency][signal] = 1
            else:
                freq_signal_dict[frequency][signal] += 1

        # sort dictionary by channel
        freq_signal_dict = {frequency: signal_count for frequency, signal_count in sorted(freq_signal_dict.items(), key=lambda item: int(item[0]))}

        youngest = [int(results[0][3]) for results in results_per_iter]
        oldest = [int(results[-1][3]) for results in results_per_iter]
        youngest = sorted(youngest)
        oldest = sorted(oldest, reverse=True)
        print(f"Youngest signals: {youngest}")
        print(f"Oldest signals: {oldest}")
        
        # TODO: replace with more robust "new result" criterium
        previous_new_result = []
        for i, signals in enumerate(signals_per_dump):
            if signals != previous_new_result:
                print(f"Result {i}: {signals}")
                previous_new_result = signals
            good_signals_amount = len(list(filter(lambda signal: signal>=MIN_SIGNAL_STRENGTH, signals)))
            good_amounts.append(good_signals_amount)
        print({x: good_amounts.count(x) for x in set(good_amounts)})

        # Variance when standing still measure
        log_variance_measure(logger, mac_signal_dict)
            
        # Signal strength per band measure
        log_strength_measure(logger, freq_signal_dict)

def log_variance_measure(logger, mac_signal_dict):
    prev_strength = 0
        
    for mac in mac_signal_dict:

        summary = ""
        distance_moved = 0
        distance_traveled = 0
        white_space_counter = 0
        log_line = "\t"
        max_strength = -100
        min_strength = 0

        # received signals, in order:
        logger.info(f"\nfrom MAC<{mac}>")
        
        for signal in mac_signal_dict[mac]:

            strength = list(signal.keys())[0] 
            count = signal[strength]
            log_line += f"{count} at {strength} dBm, "

            white_space_counter += 1
            
            if white_space_counter >= 5:
                logger.debug(log_line)
                log_line = "\t"
                white_space_counter = 0

            if prev_strength != 0:
                difference = strength - prev_strength
                summary += f"+{difference} "
                distance_moved += (difference)
                distance_traveled += abs(difference)

            max_strength = max(max_strength, strength)
            min_strength = min(min_strength, strength)
            prev_strength = strength 

        if log_line != "\t":
            logger.debug(f"{log_line}")
        
        logger.debug(f"Changes: ( {summary})")
        logger.debug(f"= {distance_moved}")
        logger.info(f"margins = {abs(min_strength)}-{abs(max_strength)} = {max_strength - min_strength} | total = {distance_traveled}")
        prev_strength = 0
        logger.debug(f"\n{'-' * 90}")

def log_strength_measure(logger, freq_signal_dict):
    signals_count = 0
    previous_freq = 0
    mid_log = ""
    end_log = ""
    mid_sum = 0
    end_sum = 0
    mid_count = 0
    end_count = 0

    logger.info("\n-----2.4GHz band-----")
    for freq in freq_signal_dict:

        if int(previous_freq) < 3000 and int(freq) > 4000:
            logger.info(f"Band total: {signals_count} signals")
            if (end_count > 0):
                logger.debug(f"Average Strength on band: ({end_log[:-1]}) / {end_count}")
                logger.info(f"= {end_sum / end_count}") 

            end_log = ""
            end_count = 0
            end_sum = 0
            signals_count = 0

            logger.info("\n-----5GHz band-----")

        logger.info(f"@{freq} MHz")

        for signal in freq_signal_dict[freq]:

            count = freq_signal_dict[freq][signal]
            logger.debug(f"\t{count} signals at {signal} dBM were received")

            signals_count += count
            mid_log += f" {count}*{signal} +"
            mid_count += count
            mid_sum += count*signal
        
        if (mid_count > 0): 
            logger.debug(f"Average Strength on channel: ({mid_log[:-1]}) / {mid_count}")
            logger.info(f"= {mid_sum / mid_count}\n")

        end_log += mid_log
        end_count += mid_count
        end_sum += mid_sum
        mid_log = ""
        mid_count = 0
        mid_sum = 0
        previous_freq = freq

    logger.info(f"Band total: {signals_count} signals")
    if (end_count > 0):
        logger.debug(f"Average Strength on band: ({end_log[:-1]}) / {end_count}")
        logger.info(f" = {end_sum / end_count}\n")