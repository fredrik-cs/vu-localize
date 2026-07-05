from queue import Queue
from threading import Thread
import time
from datetime import datetime

from src.plotresult import PlotHistogram, PlotPredictionError, PlotTable
from src.pathing import PATH_FLOOR_5, PATH_FLOOR_6, FindPosition, distance
from src.iw_interpret import Cell
from src.producer_consumer import Multilateration2D, collect_signals, consumer, single_producer, multi_producer
from src.loggers import LogBandQualities, new_logger
from src.analysis import AnalyticalDistanceToAP, PredictTrilaterate, UnityCoordinate
from src.sampling import SampleTableManager
from src.scan import FindAPs
from src.registries import RegisterFrequencies, RegisterUnknowns
from src.coordinates import GetAPUnityCoordinates, GetCoordinates, GetUnityCoordinates
from src.enums import Band
from src.makemap import PlotErrorOnFloor, PlotPathOnFloor, PlotPointsOnFloor
     
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
    floor = int(input("what floor are we analysing?\n"))
    name = input("log to what file?\n")
    logger = new_logger("draftone", name)
    error_logger = new_logger("draftone", f"{name}-error")
    result = {"ml": [], "tl": [], "mb": [], "mbf": []}
    stop_threads = False

    prod_thread = Thread(target=single_producer, args=(lambda: stop_threads,queue, Band.G2_4,))
    cons_thread = Thread(target=consumer, args=(lambda: stop_threads, queue, floor, logger, error_logger, result,))
    
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
    
    PlotPointsOnFloor(result["ml"], floor)

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
    
    floor = int(input("what floor are we analysing?\n"))
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

def ThesisDraftThree():
    ## Part 0: Setup
    # Ask for floor and filename
    floor = int(input("what floor are we analysing?\n"))
    name = input("log to what file?\n")

    # Create a logger for collection, a logger for prediction
    collect_logger = new_logger("draftthree", f"{name}-collect")
    predict_logger = new_logger("draftthree", f"{name}-predict")
    
    collect_thread = Thread(target=collect_signals, args=(collect_logger, floor, lambda: stop_threads))
    stop_threads = False

    # Give timer
    time.sleep(1)
    print("Start in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("GO!")

    ## Part 1: Collection
    # Keep scanning until enter is pressed
    collect_thread.start()
    time.sleep(5)
    input("Press enter to finish course")
    
    stop_threads = True


    ## Part 2: Simulation
    # Read back your log, line for line
    lines = []
    with open(f"experiments/draftthree/{name}-collect.log") as f:
        lines = f.readlines()

    begin_ts = int(lines[0].split()[2])
    end_ts = int(lines[-2].split()[2])
    duration_in_ns = end_ts - begin_ts 
    last_second = begin_ts
    cells_in_second24 = 0
    cells_in_second50 = 0
    predictions_in_second24 = 0
    predictions_in_second50 = 0

    def FindRealLocation(timestamp: int):
        percentage = (ts - begin_ts) / duration_in_ns
        actual_coord = FindPosition(floor, percentage)
        return actual_coord

    def FindError(actual_coord: tuple, predicted_coord: UnityCoordinate):
        return distance(actual_coord, (predicted_coord.x, predicted_coord.z))
    

    # File signals into their respective buckets (2.4/5G, >-80,>-70>-67)
    prediction_buckets: dict[str, list[list]] = {
        "24-ALL-tri": [],
        "24-80-tri": [],
        "24-70-tri": [],
        "24-67-tri": [],
        "50-ALL-tri": [],
        "50-80-tri": [],
        "50-70-tri": [],
        "50-67-tri": [],
        "24-ALL-mul": [],
        "24-80-mul": [],
        "24-70-mul": [],
        "24-67-mul": [],
        "50-ALL-mul": [],
        "50-80-mul": [],
        "50-70-mul": [],
        "50-67-mul": []
    }

    for i in range(int(len(lines)/2)):
        signal_buckets: dict[str, list[Cell]] = {
        "24-ALL": [],
        "24-80": [],
        "24-70": [],
        "24-67": [],
        "50-ALL": [],
        "50-80": [],
        "50-70": [],
        "50-67": []
        }

        def AddToBucket(freq: str, cell: Cell):
            if cell.signal >= -67:
                signal_buckets[f"{freq}-67"].append(cell)
            if cell.signal >= -70:
                signal_buckets[f"{freq}-70"].append(cell)
            if cell.signal > -80:
                signal_buckets[f"{freq}-80"].append(cell)
            signal_buckets[f"{freq}-ALL"].append(cell)

        timestamp_line = lines[2*i]
        cell_count24 = int(timestamp_line.split()[0])
        cells_in_second24 += cell_count24
        cell_count50 = int(timestamp_line.split()[1])
        cells_in_second50 += cell_count50
        ts = int(timestamp_line.split()[2])
        signal_info = lines[2*i+1]
        signal_dict = eval(signal_info)
        # cell_list = map(signal_dict)

        for i, frequency in enumerate(signal_dict["frequencies"]):
            cell = Cell()
            cell.frequency = frequency
            cell.name = signal_dict["names"][i]
            cell.signal = signal_dict["signals"][i]
            cell.timestamp
            if frequency < 5000:
                AddToBucket("50", cell)
            else:
                AddToBucket("24", cell)

        # Whenever a bucket can do trilateration, make the prediction
        for bucket_tag in signal_buckets:
            bucket = signal_buckets[bucket_tag]
            bucket = sorted(bucket, key=lambda c: c.timestamp, reverse=True)

            if len(bucket) >= 3:
                GetAPUnityCoordinates(bucket)
                for cell in bucket:
                    cell.distance = AnalyticalDistanceToAP(cell.signal)
                bucket_coords = [UnityCoordinate(*cell.coords) for cell in bucket]
                bucket_distances = [cell.distance for cell in bucket]
                predicted_coord = Multilateration2D(bucket_coords, bucket_distances)
                # Use the ts to find the percentage of the way into the path you are, then calculate error
                actual_coord = FindRealLocation(ts)
                error = FindError(actual_coord, predicted_coord)

                # File the prediction in a dictionary, with error, timestamp, AP names, AP locations and distances.
                # Whenever a bucket can do multilateration, do so with as many signals as possible
                # File this prediction similarly
                def AddToPredictionBucket(prediction: UnityCoordinate, reality: tuple, algorithm:str, error: int, bucket: list[Cell]):
                    prediction_tag = bucket_tag+algorithm
                    bucket_names = [cell.name for cell in bucket]
                    bucket_coords = [UnityCoordinate(*cell.coords) for cell in bucket]
                    bucket_signals = [cell.signal for cell in bucket]
                    prediction_info = [prediction, reality, error, ts, bucket_names, bucket_coords, bucket_signals]
                    prediction_buckets[prediction_tag].append(prediction_info)

                if len(bucket) == 3:
                    AddToPredictionBucket(predicted_coord, actual_coord, "-tri", error, bucket)
                    if bucket_tag[0] == "2":
                        predictions_in_second24 += 1
                    else:
                        predictions_in_second50 += 1
                else:
                    AddToPredictionBucket(predicted_coord, actual_coord, "-mul", error, bucket)
                    bucket = bucket[:3]
                    bucket_coords = [UnityCoordinate(*cell.coords) for cell in bucket]
                    bucket_distances = [cell.distance for cell in bucket]
                    predicted_coord = Multilateration2D(bucket_coords, bucket_distances)
                    # Use the ts to find the percentage of the way into the path you are, then calculate error
                    actual_coord = FindRealLocation(ts)
                    error = FindError(actual_coord, predicted_coord)
                    AddToPredictionBucket(predicted_coord, actual_coord, "-tri", error, bucket)

                    if bucket_tag[0] == "2":
                        predictions_in_second24 += 2
                    else:
                        predictions_in_second50 += 2

            # If a bucket cannot do either, take the previous prediction(s!) and calculate the new error
            else:
                tag_tri = bucket_tag+"-tri"
                tag_mul = bucket_tag+"-mul"
                if prediction_buckets[tag_tri]:
                    last_prediction = prediction_buckets[tag_tri][-1].copy()
                    predicted_coord = last_prediction[0]
                    actual_coord = FindRealLocation(ts)
                    error = FindError(actual_coord, predicted_coord)
                    last_prediction[1] = actual_coord
                    last_prediction[2] = error
                    prediction_buckets[tag_tri].append(last_prediction)
                
                if prediction_buckets[tag_mul]:
                    last_prediction = prediction_buckets[tag_mul][-1].copy()
                    predicted_coord = last_prediction[0]
                    actual_coord = FindRealLocation(ts)
                    error = FindError(actual_coord, predicted_coord)
                    last_prediction[1] = actual_coord
                    last_prediction[2] = error
                    prediction_buckets[tag_mul].append(last_prediction)
    
        # Whenever a second passes, for every bucket store the amount of new signals it got and new predictions made
        if ts - last_second >= 1e9:
            readable_time = datetime.fromtimestamp(float(last_second) / 1e9)
            formatted_time = readable_time.strftime('%H:%M:%S')
            predict_logger.info(f"in the second of {formatted_time}:")
            predict_logger.info(f"\t{cells_in_second24} new cells on 2.4 GHz, {cells_in_second50} new cells on 5 GHz")
            predict_logger.info(f"\t{predictions_in_second24} new predictions on 2.4 GHz, {predictions_in_second50} new predictions on 5 GHz")

            last_second = ts
            cells_in_second24 = 0
            cells_in_second50 = 0
            predictions_in_second24 = 0
            predictions_in_second50 = 0


    # Log each bucket at the end sequentially
    for bucket_tag in prediction_buckets:
        bucket = prediction_buckets[bucket_tag]
        predict_logger.info(f"{bucket_tag}")
        for prediction in bucket:
            predict_logger.info(f"{prediction}")

    ## Part 3: Plot
    # For every bucket, find the average and worst error, average and worst predictions count (and signals count?) per second
    data: list[list[str]] = []
    for bucket_tag in prediction_buckets:
        
        bucket = prediction_buckets[bucket_tag]
        total_error = 0
        worst_error = 0

        if(len(bucket) > 0):
            for item in bucket:
                error = item[2]
                total_error += error
                worst_error = max(error, worst_error)
            average_error = round(total_error / len(bucket), 3)
            worst_error = round(worst_error, 3)
        else:
            average_error = float('nan')
            worst_error = float('nan')

        data.append([f"{average_error:.3f}", f"{worst_error:.3f}"])
        # data.append(str(average_error))
        # data.append(str(worst_error))

    # Make a table on that
    PlotTable(data, name)
    # For every bucket, make a scatterplot connecting the real locations to the predicted locations with a line
    PlotPredictionError()
    # Might need to skip some timestamps for that one
    # Histograms of errors in x, z, and distance?
    PlotHistogram()

def PlotErrors():
    name = input("Which file are we plotting?\n")
    floor = input("What floor are is this data from?\n")
    lines = []
    with open(f"experiments/draftone/{name}.log") as f:
        lines = f.readlines()
    # print(lines)
    for line in lines:
        # print(line)
        if line[0] != '{':
            continue
        log_dict = eval(line)
        if "prediction" not in log_dict:
            log_dict["prediction"] = []
        PlotErrorOnFloor(log_dict["coordinates"], log_dict["distances"], floor, log_dict["prediction"])

def PlotFloorPaths():
    path5 = PATH_FLOOR_5
    path6 = PATH_FLOOR_6
    PlotPathOnFloor(path5, 5)
    PlotPathOnFloor(path6, 6)