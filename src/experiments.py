from queue import Queue
from threading import Thread
import time

from src.iw_interpret import Cell
from src.producer_consumer import consumer, single_producer, multi_producer
from src.loggers import LogBandQualities, new_logger
from src.analysis import PredictTrilaterate
from src.sampling import SampleTableManager
from src.scan import FindAPs
from src.registries import RegisterFrequencies, RegisterUnknowns
from src.coordinates import GetCoordinates, GetUnityCoordinates
from src.enums import Band
from src.makemap import PlotPointsOnFloor
     
def ScanFloor(interface, ssids):

    selected_floor = input("Are you scanning floor 5 or 6? ")
    if (selected_floor != '5') and (selected_floor != '6'):
        raise Exception("Invalid floor provided")
    selected_floor = int(selected_floor)
    
    frequencies = input("What band are you scanning on? Select 1-4\n   1) 2.4 GHz\n   2) 5 GHz\n   3) Both\n   4) All (Not recommended)\n")
    match frequencies:
        case '1': frequencies = Band.G2_4
        case '2': frequencies = Band.G5
        case '3': frequencies = Band.BOTH
        case '4': frequencies = Band.ALL
        case _: raise Exception("Invalid band provided, please select between 1-3")

    coordinates = GetCoordinates(selected_floor)
    unity_coordinates = GetUnityCoordinates(selected_floor)
    cardinals = ["North", "East", "South", "West"]
    table_manager = SampleTableManager(selected_floor)
    
    for i, coordinate in enumerate(coordinates):
        unity_coordinate = unity_coordinates[i]
        floor = coordinate.floor
        x = coordinate.x
        y = coordinate.y 
        
        input(f"Press any key at ({x}, {y}) [floor {floor}]")
        for cardinal in cardinals:
            
            input(f"Press any key while facing {cardinal}")
            for i in range(4):
                valids, unknowns = FindAPs(ssids, frequencies, interface, min_aps=3)
                RegisterUnknowns(unknowns)    # type: ignore
                RegisterFrequencies(valids) # type: ignore
                # Multilateration requires at least 3 points, which is trilateration.
                # If the program goes this way it might be a good idea to keep scanning until there are at least 3 matches.
                # TODO: Look into multilateration for localization
                wpe, ape = PredictTrilaterate(valids, unity_coordinate)
                table_manager.AddSample(unity_coordinate, cardinal, valids, ape, wpe)
                
        table_manager.WriteCSV()

def ThesisDraftZero():

    file_name = input("log to what files?\n")
    
    LogBandQualities(Band.ALL,   f"all-{file_name}"     )
    LogBandQualities(Band.G2_4,  f"twofour-{file_name}" )
    LogBandQualities(Band.G5,    f"fiveo-{file_name}"   ) 

def ThesisDraftOne():
    queue: Queue[list[Cell]] = Queue()
    floor = int(input("what floor are we analysing?"))
    name = input("log to what file?\n")
    logger = new_logger("draftone", name)
    result = {"ml": [], "tl": [], "mb": [], "mbf": []}
    stop_threads = False

    prod_thread = Thread(target=single_producer, args=(lambda: stop_threads,queue, Band.G2_4,))
    cons_thread = Thread(target=consumer, args=(lambda: stop_threads, queue, floor, logger, result,))
    
    prod_thread.start()
    time.sleep(1)
    print("Start in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("GO!")
    cons_thread.start()
    
    time.sleep(5)
    input("Press enter to finish course")
    
    stop_threads = True
    prod_thread.join()
    cons_thread.join()
    
    PlotPointsOnFloor(result, floor)

def ThesisDraftTwo():
    queue_all: Queue[list[Cell]] = Queue()
    # queue_80: Queue[list[Cell]] = Queue()
    queue_70: Queue[list[Cell]] = Queue()
    # queue_67: Queue[list[Cell]] = Queue()
    queue_5k: Queue[list[Cell]] = Queue()
    queues_and_rules = [(queue_all, -100, 0, 5000),
                    #    (queue_80, -81, 0, 5000),
                       (queue_70, -71, 0, 5000),
                    #    (queue_67, -68, 0, 5000),
                       (queue_5k, -100, 4000, 10000)]
    
    floor = int(input("what floor are we analysing?"))
    name = input("log to what file?\n")
    logger_all = new_logger("drafttwo", "all_"+name)
    # logger_80 = new_logger("drafttwo", "80_"+name)
    logger_70 = new_logger("drafttwo", "70_"+name)
    # logger_67 = new_logger("drafttwo", "67_"+name)
    logger_5k = new_logger("drafttwo", "5k_"+name)
    result_all = {"ml": [], "tl": [], "mb": [], "mbf": []}
    # result_80 = {"ml": [], "tl": [], "mb": [], "mbf": []}
    result_70 = {"ml": [], "tl": [], "mb": [], "mbf": []}
    # result_67 = {"ml": [], "tl": [], "mb": [], "mbf": []}
    result_5k = {"ml": [], "tl": [], "mb": [], "mbf": []}
    stop_threads = False

    prod_thread = Thread(target=multi_producer, args=(lambda: stop_threads, queues_and_rules,  Band.G2_4,))
    cons_all = Thread(target=consumer, args=(lambda: stop_threads, queue_all, floor, logger_all,  result_all,))
    # cons_80 = Thread(target=consumer, args=(lambda: stop_threads, queue_80, floor, logger_80,  result_80,))
    cons_70 = Thread(target=consumer, args=(lambda: stop_threads, queue_70, floor, logger_70,  result_70,))
    # cons_67 = Thread(target=consumer, args=(lambda: stop_threads, queue_67, floor, logger_67,  result_67,))
    cons_5k = Thread(target=consumer, args=(lambda: stop_threads, queue_5k, floor, logger_5k,  result_5k,))
    
    prod_thread.start()
    time.sleep(1)
    print("Start in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("GO!")
    cons_all.start()
    # cons_80.start()
    cons_70.start()
    # cons_67.start()
    cons_5k.start()

    time.sleep(5)
    input("Press enter to finish course")

    stop_threads = True
    prod_thread.join()
    cons_all.join()
    # cons_80.join()
    cons_70.join()
    # cons_67.join()
    cons_5k.join()

    PlotPointsOnFloor(result_all, floor)
    # PlotPointsOnFloor(result_80, floor)
    PlotPointsOnFloor(result_70, floor)
    # PlotPointsOnFloor(result_67, floor)
    PlotPointsOnFloor(result_5k, floor)