from src.trilateration import AnalyticalDistanceToAP, Trilaterate3D, Trilaterate3DAlternate 
from src.coordinates import GetAPUnityCoordinates
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
                for cell in combo:
                    cell.distance = AnalyticalDistanceToAP(cell.signal)
                predicted_coord = Trilaterate3DAlternate(combo[0].coords, combo[1].coords, combo[2].coords,
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