from itertools import combinations
import statistics
from coordinates import GetAPUnityCoordinates, GetCoordinates, GetUnityCoordinates
from enums import Band, SSIDs, WifiInterface
from sampling import SampleTableManager
from scan import FindAPs
from loggers import LogFrequencies, LogUnknowns
from trilateration import AnalyticalDistanceToAP, Trilaterate3D    
  
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
                valids, unknowns = FindAPs(ssid, frequencies, interface)
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
    
    floor = int(input("Are you scanning floor 5 or 6? "))
    if (floor != 5) and (floor != 6):
        raise Exception("Invalid floor provided")
    
    ScanFloor(interface, ssid, 5, Band.ALL)