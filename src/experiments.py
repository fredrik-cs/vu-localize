from loggers import LogBandQualities
from src.analysis import PredictTrilaterate
from src.sampling import SampleTableManager
from src.scan import FindAPs
from src.registries import RegisterFrequencies, RegisterUnknowns
from src.coordinates import GetCoordinates, GetUnityCoordinates
from src.enums import Band
     
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
    
    LogBandQualities(Band.ALL, "all-"+file_name)
    LogBandQualities(Band.G2_4, "twofour-"+file_name)
    LogBandQualities(Band.G5, "fiveo-"+file_name) 

def ThesisDraftOne(interface, ssid):
    pass