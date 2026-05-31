from datetime import datetime
from logging import Logger
import logging
import time
from queue import Queue

from src.coordinates import GetAPUnityCoordinates, MeterToUnity, UnityCoordinate
from src.trilateration import AnalyticalDistanceToAP, Multilateration2D, Trilaterate3DAlternate, MobileTrilateration
from src.scan import FilterAPs
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
        

def consumer(stopped, queue: Queue[list[Cell]], floor: int, logger: Logger, results: list):
    
    level = logging.INFO
    logging.basicConfig(level=level, format="%(message)s")

    while not stopped():
        
        try:
            message = queue.get()
            
            process_message(message, results, logger, floor)
            print(results)

            time.sleep(AS_ITERATIONS * AS_SLEEP_DURATION)

        except Exception as e:
            # raise e
            
            print(e)
            time.sleep(AS_ITERATIONS * AS_SLEEP_DURATION)

def process_message(message, results, logger, floor):
    timestamp = time.time_ns()

    message = sorted(message, key= lambda cell: cell.age)
    # print(message)

    # Get cells with unique addresses, not names?
    seen = set()
    cells = []
    for cell in message:
        if cell.address not in seen:
            cells.append(cell)
            seen.add(cell.address)

    # Get location of APs (mac -> name -> coords)
    named_APs, _ = FilterAPs(cells)
    GetAPUnityCoordinates(named_APs)

    # Get distance of APs
    for cell in named_APs:
        cell.distance = AnalyticalDistanceToAP(cell.signal)

    # Sort APs for different algos
    floor_APs = list(filter(lambda cell: cell.name[6] == f'{floor}', named_APs))
    if len(floor_APs) < 3:
        time.sleep(AS_ITERATIONS * AS_SLEEP_DURATION)
        return 
    first_three = named_APs[:3]
    floor_three = floor_APs[:3]
    first_four = named_APs[:4]
    floor_four = floor_APs[:4]

    # Translate coordinate representation
    ml_coords = [UnityCoordinate(*cell.coords) for cell in floor_APs]
    ml_distances = [MeterToUnity(cell.distance) for cell in floor_APs]
    tl_coords = [UnityCoordinate(*cell.coords) for cell in first_three]
    tl_distances = [MeterToUnity(cell.distance) for cell in first_three]
    t3_coords = [UnityCoordinate(*cell.coords) for cell in floor_three]
    t3_distances = [MeterToUnity(cell.distance) for cell in floor_three]
    mb_coords = [UnityCoordinate(*cell.coords) for cell in first_four]
    mb_distances = [MeterToUnity(cell.distance) for cell in first_four]
    mbf_coords = [UnityCoordinate(*cell.coords) for cell in floor_four]
    mbf_distances = [MeterToUnity(cell.distance) for cell in floor_four]

    # print(t3_coords, t3_distances)

    # Triangulate
    ml_predicted_coord = Multilateration2D(ml_coords, ml_distances)
    tl_predicted_coord = Trilaterate3DAlternate(*tl_coords, *tl_distances)
    t3_predicted_coord = Trilaterate3DAlternate(*t3_coords, *t3_distances)
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
    print(results)

    # New logger
    def log_cell_list(cell_list: list[Cell]):
        logger.info(f"from cells:")
        for cell in cell_list:
            ts = timestamp - cell.age * 1_000_000
            cell_time = datetime.fromtimestamp(float(ts) / 1e9)
            logger.info(f"\tTS: {cell_time}, Name: {cell.name}")
            logger.info(f"\tSignal: {cell.signal} dBm, {cell.frequency} MHz")

    # Log results
    logger.info(f"Time of log: {datetime.now()}")
    logger.info(f"got {ml_predicted_coord} using 2D multilateration")
    log_cell_list(floor_APs)
    logger.info(f"got {tl_predicted_coord} from 3D Trilateration")
    log_cell_list(first_three)
    # logger.info(f"got {t3_predicted_coord} from floor specific 3D Trilateration")
    # log_cell_list(floor_three)
    logger.info(f"got {mb_predicted_coord} from Mobile Trilateration")
    log_cell_list(first_four)
    logger.info(f"got {mbf_predicted_coord} from floor specific Mobile Trilateration")
    log_cell_list(floor_four)
        
