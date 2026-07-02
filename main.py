import argparse

from src.enums import SSIDs, WifiInterface, Experiment
from src.experiments import PlotErrors, ScanFloor, ThesisDraftZero, ThesisDraftOne, ThesisDraftTwo
  
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true')
    parser.add_argument('-p', action='store_true')
    args = parser.parse_args()
    
    selected_arguments = Experiment.DRAFT_ONE
    if args.p:
        selected_arguments = Experiment.PLOT_ERRORS
        # print("Plot!")
    elif args.d:
        # print("Draft!")
        selected_arguments = Experiment.DRAFT_ONE

    interface = WifiInterface.WLP1S0
    ssid = [SSIDs.VU_CAMPUSNET, SSIDs.EDUROAM, SSIDs.IOTROAM]
    
    match selected_arguments:
        case Experiment.PLOT_ERRORS:
            PlotErrors()
        case Experiment.SCAN_FLOOR:
            ScanFloor(interface, ssid)
        case Experiment.DRAFT_ZERO:
            ThesisDraftZero()
        case Experiment.DRAFT_ONE:
            ThesisDraftOne()
        case Experiment.DRAFT_TWO:
            ThesisDraftTwo()

