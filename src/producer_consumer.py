from datetime import datetime
from logging import Logger
import logging
import time
from queue import Queue

from src.coordinates import GetAPUnityCoordinates, UnityCoordinate
from src.trilateration import AnalyticalDistanceToAP, Multilateration2D, Trilaterate3D, Trilaterate3DAlternate, MobileTrilateration
from src.scan import FilterAPs, FindNames
from src.iw_interpret import Cell

AS_SLEEP_DURATION = 0.01
AS_ITERATIONS = 10

def single_producer(stopped, queue: Queue[list[Cell]], band = []):
    # Trigger and dump scan results for main thread to consume when necessary
    while not stopped():
        unfiltered_cells: list[Cell] = []

        for i in range(AS_ITERATIONS):
            Cell.trigger_scan(band)
            cell_dump = Cell.dump_scan()
            unfiltered_cells.extend(cell_dump)
            time.sleep(AS_SLEEP_DURATION)

        good_cells = list(filter(lambda cell: cell.signal>=-100, unfiltered_cells))
        good_cells = list(filter(lambda cell: cell.frequency<5000, good_cells))
        
        queue.put(good_cells)

def multi_producer(stopped, queues_and_rules: list[tuple[Queue[list[Cell]], int, int, int]], band = []):
    
    while not stopped():
        cells = [[] for q in queues_and_rules]

        for i in range (AS_ITERATIONS):
            Cell.trigger_scan(band)
            cell_dump = Cell.dump_scan()
            for j, tuple in enumerate(queues_and_rules):
                
                new_cells = []
                addresses = [cell.address for cell in cells[j]]
                for cell in cell_dump:
                    index_of_last = 0
                    if cell.address in addresses:
                        index_of_last = (len(cells[j]) - 1) - list(map(lambda cell: cell.address, cells[j][::-1])).index(cell.address)
                    if cell.address not in addresses or cell.age < cells[j][index_of_last].age:
                        new_cells.append(cell)
                        addresses.append(cell.address)
                    else:
                        cells[j][index_of_last].age = cell.age

                proper_cells = list(
                    filter(lambda cell: 
                        cell.signal > tuple[1] and
                        cell.frequency > tuple[2] and
                        cell.frequency > tuple[3],
                    new_cells))
                # if cell_dump[k].address is not in cells[j] 
                # or cell_dump[k].age < age of last cell in cells[j] with the same address,
                # then add to new
                # else change age of cell in cells[j]
                cells[j].extend(proper_cells)
                time.sleep(AS_SLEEP_DURATION)
        

def consumer(stopped, queue: Queue[list[Cell]], floor: int, logger: Logger, error_logger: Logger, results: list):
    
    level = logging.INFO
    logging.basicConfig(level=level, format="%(message)s")

    while not stopped():
        
        try:
            message = queue.get()
            
            process_message(message, results, logger, error_logger, floor)
            # print(results)

            time.sleep(AS_ITERATIONS * AS_SLEEP_DURATION)

        except Exception as e:
            print(e)
            time.sleep(AS_ITERATIONS * AS_SLEEP_DURATION)

def process_message(message, results, logger:Logger, error_logger:Logger, floor):
    timestamp = time.time_ns()

    message = sorted(message, key= lambda cell: cell.age)

    named_APs, _ = FilterAPs(message)

    # Get cells with unique names
    seen = set()
    unique_cells = []
    for cell in named_APs:
        if cell.name not in seen:
            unique_cells.append(cell)
            seen.add(cell.name)

    print(unique_cells)

    GetAPUnityCoordinates(unique_cells)

    # Get distance of APs
    for cell in unique_cells:
        cell.distance = AnalyticalDistanceToAP(cell.signal)

    # Sort APs for different algos
    floor_APs = list(filter(lambda cell: cell.name[6] == f'{floor}', unique_cells))
    if len(floor_APs) < 3:
        print(f"Too little APs: {floor_APs}")
        return 
    
    unique_cells = sorted(unique_cells, key= lambda cell: cell.distance)
    floor_APs = sorted(floor_APs, key= lambda cell: cell.distance)

    first_three = unique_cells[:3]
    floor_three = floor_APs[:3]
    first_four = unique_cells[:4]
    floor_four = floor_APs[:4]

    # Translate coordinate representation
    ml_coords = [UnityCoordinate(*cell.coords) for cell in floor_APs]
    ml_distances = [cell.distance for cell in floor_APs]
    tl_coords = [UnityCoordinate(*cell.coords) for cell in first_three]
    tl_distances = [cell.distance for cell in first_three]
    t3_coords = [UnityCoordinate(*cell.coords) for cell in floor_three]
    t3_distances = [cell.distance for cell in floor_three]
    mb_coords = [UnityCoordinate(*cell.coords) for cell in first_four]
    mb_distances = [cell.distance for cell in first_four]
    mbf_coords = [UnityCoordinate(*cell.coords) for cell in floor_four]
    mbf_distances = [cell.distance for cell in floor_four]

    # Triangulate
    ml_predicted_coord = Multilateration2D(ml_coords, ml_distances)
    tl_predicted_coord = Trilaterate3DAlternate(*tl_coords, *tl_distances)
    t3_predicted_coord = Multilateration2D(t3_coords, t3_distances)
    mb_predicted_coord = MobileTrilateration(mb_coords, mb_distances)
    mbf_predicted_coord = MobileTrilateration(mbf_coords, mbf_distances)

    # Save non-error results
    if ml_predicted_coord.x > 0 and ml_predicted_coord.z > 0:
        results["ml"].append((ml_predicted_coord.x, ml_predicted_coord.z))
    if tl_predicted_coord.x > 0 and tl_predicted_coord.z > 0:
        results["tl"].append((tl_predicted_coord.x, tl_predicted_coord.z))
    if mb_predicted_coord.x > 0 and mb_predicted_coord.z > 0:
        results["mb"].append((mb_predicted_coord.x, mb_predicted_coord.z))
    if mbf_predicted_coord.x > 0 and mbf_predicted_coord.z > 0:
        results["mbf"].append((mbf_predicted_coord.x, mbf_predicted_coord.z))

    # New logger
    def log_cell_list(name_algorithm: str, predicted_coord:UnityCoordinate, cell_list: list[Cell]):
        log_dict = {
            "algorithm": name_algorithm,
            "coordinates": [cell.coords for cell in cell_list],
            "distances": [cell.distance for cell in cell_list],
            "names": [cell.name for cell in cell_list],
            "timestamps": [str(datetime.fromtimestamp(float(timestamp - cell.age * 1_000_000) / 1e9)) for cell in cell_list],
            "signals": [cell.signal for cell in cell_list],
            "frequencies": [cell.frequency for cell in cell_list],
        }
        if predicted_coord.x < 0:
            error_logger.info(log_dict)
        else:
            log_dict["prediction"] = predicted_coord
            logger.info(log_dict)

    def log_cell_list_verbose(cell_list: list[Cell]):
        logger.info(f"from cells:")
        for cell in cell_list:
            ts = timestamp - cell.age * 1_000_000
            cell_time = datetime.fromtimestamp(float(ts) / 1e9)
            logger.info(f"\tTS: {cell_time}, Name: {cell.name}")
            logger.info(f"\tSignal: {cell.signal} dBm, {cell.frequency} MHz")

    # Log results
    VERBOSE = False

    if VERBOSE:
        logger.info(f"Time of log: {datetime.now()}")
        logger.info(f"got {ml_predicted_coord} using 2D multilateration")
        log_cell_list_verbose(floor_APs)
        logger.info(f"got {t3_predicted_coord} from floor specific 3D Trilateration")
        log_cell_list_verbose(floor_three)

    else:
        logger.info(datetime.now())
        log_cell_list("ml",ml_predicted_coord, floor_APs)
        log_cell_list("t3", t3_predicted_coord, floor_three)
            
def collect_signals(logger: Logger, floor: int, stopped):
    young_unique_cells: dict[tuple, Cell] = {}
    unique_name_frequency_pairs = set()

    # Keep track of new names per band, and when those names get younger signals. 
    # The count of this is the amount of signals per band
    unique_cell_count24 = 0
    unique_cell_count50 = 0

    forbidden_names = ["NU-AP05385", 
    "NU-AP05384", 
    "NU-AP05383", 
    "NU-AP05382", 
    "NU-AP05381", 
    "NU-AP05380", 
    "NU-AP05379", 
    "NU-AP05378", 
    "NU-AP05377", 
    "NU-AP05376", 
    "NU-AP05375", 
    "NU-AP05374", 
    "NU-AP05373", 
    "NU-AP05372"] 

    while not stopped():
        Cell.trigger_scan([])
        cell_dump = Cell.dump_scan()
        timestamp = time.time_ns()
        named_cells = filter(lambda cell: cell.name != "" and (cell.name not in forbidden_names), FindNames(cell_dump))
        floor_cells = filter(lambda cell: cell.name[:7] == f"NU-AP0{floor}", named_cells)
        pairs_altered = set()

        for cell in floor_cells:
            pair = (cell.name, cell.frequency)

            if pair not in unique_name_frequency_pairs:
                unique_name_frequency_pairs.add(pair)
                cell.timestamp = timestamp - cell.age * 1e6 
                young_unique_cells[pair] = cell
                pairs_altered.add(pair)
            elif timestamp - cell.age * 1e6 > young_unique_cells[(cell.name, cell.frequency)].timestamp:
                cell.timestamp = timestamp - cell.age * 1e6 
                young_unique_cells[pair] = cell
                pairs_altered.add(pair)
            else:
                continue
        
        new_cell_count24 = len(list(filter(lambda pair: pair[1] < 5000, pairs_altered)))
        unique_cell_count24 += new_cell_count24
        new_cell_count50 = len(list(filter(lambda pair: pair[1] > 4999, pairs_altered)))
        unique_cell_count50 += new_cell_count50

        removable_pairs = []
        if new_cell_count24 > 0 or new_cell_count50 > 0:
            names = []
            addresses = []
            ssids = []
            signals = []
            timestamps = []
            frequencies = []

            for pair in young_unique_cells:
                curr_cell = young_unique_cells[pair]
                # print(curr_cell)

                if (timestamp - curr_cell.timestamp) > (6 * 1e9):
                    print(f"discarded readings from {curr_cell.name} for old age of {((timestamp-curr_cell.timestamp) / 1e9):.3f} seconds")
                    removable_pairs.append(pair)
                    continue

                names.append(curr_cell.name)
                addresses.append(curr_cell.address)
                ssids.append(curr_cell.ssid)
                signals.append(curr_cell.signal)
                timestamps.append(curr_cell.timestamp)
                frequencies.append(curr_cell.frequency)
            
            for pair in removable_pairs:
                young_unique_cells.pop(pair)
                unique_name_frequency_pairs.remove(pair)

            # Log time and the set of youngest received signals with unique name,frequency pairs that were collected within 6 seconds
            # For the signal log name, mac, ssid, signal strength, timestamp, frequency
            
            cell_log = {
                "names": names,
                "addresses": addresses,
                "ssids": ssids,
                "signals": signals,
                "timestamps": timestamps,
                "frequencies": frequencies
            }
            logger.info(f"{unique_cell_count24} {unique_cell_count50} {timestamp}")
            logger.info(f"{cell_log}")

        time.sleep(AS_SLEEP_DURATION)