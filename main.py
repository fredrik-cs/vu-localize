from itertools import combinations
import statistics
from src.coordinates import GetAPUnityCoordinates, GetCoordinates, GetUnityCoordinates
from src.enums import Band, SSIDs, WifiInterface
from src.sampling import SampleTableManager
from src.scan import FindAPs
from src.loggers import LogFrequencies, LogUnknowns
from src.trilateration import AnalyticalDistanceToAP, Trilaterate3D    
  
def PredictTrilaterate(valids, unity_coordinate):
    worst_predicted_error = -1
    average_predicted_error = -1
    
    if len(valids) > 2:
        predicted_coords = []
        GetAPUnityCoordinates(valids)
        #TODO: Make a strategy for selecting 3 APs
        combos = list(combinations(valids, 3))
        for combo in combos:
            try:
                for cell in combo:
                    cell.distance = AnalyticalDistanceToAP(cell.signal)
                predicted_coord = Trilaterate3D(combo[0].coords, combo[1].coords, combo[2].coords,
                            combo[0].distance, combo[1].distance, combo[2].distance)
                predicted_coords.append(predicted_coord)
            except Exception as e:
                #TODO: Why are there division by zero errors?
                # print(e)
                pass
        try:
            #This errors when there aren't any predicted coords. This happens if all combos errored.
            distances = [p.distance(unity_coordinate) for p in predicted_coords]
            worst_predicted_error = max(distances)
            best_predicted_error = min(distances)
            average_predicted_error = statistics.mean(distances)
            print(f"Worst: {worst_predicted_error}")
            print(f"Average: {average_predicted_error}")
            print(f"Best: {best_predicted_error}")
            
        except Exception as e:
            print(e)
            pass
    
    return worst_predicted_error, average_predicted_error
        
def ScanFloor(interface, ssid, selected_floor, frequencies = []):
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
                valids, unknowns = FindAPs(ssid, frequencies, interface, min_aps=3)
                LogUnknowns(unknowns)
                LogFrequencies(valids)
                # Multilateration requires at least 3 points, which is trilateration.
                # If the program goes this way it might be a good idea to keep scanning until there are at least 3 matches.
                # TODO: Look into multilateration for localization
                wpe, ape = PredictTrilaterate(valids, unity_coordinate)
                table_manager.AddSample(unity_coordinate, cardinal, valids, ape, wpe)
                
        table_manager.WriteCSV()
        
                 
if __name__ == "__main__":
    interface = WifiInterface.WLP1S0
    ssid = SSIDs.VU_CAMPUSNET
    
    floor = input("Are you scanning floor 5 or 6? ")
    if (floor != '5') and (floor != '6'):
        raise Exception("Invalid floor provided")
    floor = int(floor)
    
    band = input("What band are you scanning on? Select 1-4\n   1) 2.4 GHz\n   2) 5 GHz\n   3) Both\n   4) All (Not recommended)\n")
    match band:
        case '1': band = Band.G2_4
        case '2': band = Band.G5
        case '3': band = Band.BOTH
        case '4': band = Band.ALL
        case _: raise Exception("Invalid band provided, please select between 1-3")
    
    ScanFloor(interface, ssid, floor, band)
