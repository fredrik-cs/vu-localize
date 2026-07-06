import argparse

from src.enums import SSIDs, WifiInterface, Experiment
from src.experiments import FindNewAPs, PlotErrors, PlotFloorPaths, ScanFloor, ThesisDraftThree, ThesisDraftZero, ThesisDraftOne, ThesisDraftTwo
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-o', action='store_true')
    parser.add_argument('-p', action='store_true')
    parser.add_argument('-e', action='store_true')
    args = parser.parse_args()
    
    selected_arguments = Experiment.DRAFT_THREE

    if args.f:
        selected_arguments = Experiment.FIND_NEW
    if args.o:
        selected_arguments = Experiment.DRAFT_ONE
    elif args.p:
        selected_arguments = Experiment.PLOT_PATHS
    elif args.e:
        selected_arguments = Experiment.PLOT_ERRORS

    interface = WifiInterface.WLP2S0
    ssid = [SSIDs.VU_CAMPUSNET, SSIDs.EDUROAM, SSIDs.IOTROAM]
    
    match selected_arguments:
        case Experiment.FIND_NEW:
            FindNewAPs()
        case Experiment.PLOT_PATHS:
            PlotFloorPaths()
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
        case Experiment.DRAFT_THREE:
            ThesisDraftThree()