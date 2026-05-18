from src.trilateration import AnalyticalDistanceToAP, Trilaterate3D, Trilaterate3DAlternate 
from src.coordinates import GetAPUnityCoordinates, UnityCoordinate
from itertools import combinations


import statistics

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
                coords: list[UnityCoordinate] = []
                distances = []
                for cell in combo:
                    distances.append(AnalyticalDistanceToAP(cell.signal))
                    coords.append(UnityCoordinate(*cell.coords))
                predicted_coord = Trilaterate3DAlternate(coords[0], coords[1], coords[2],
                            distances[0], distances[1], distances[2])
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