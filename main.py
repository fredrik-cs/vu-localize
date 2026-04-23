from src.enums import SSIDs, WifiInterface, Experiment
from src.experiments import ScanFloor, ThesisDraftZero, ThesisDraftOne
  
        
if __name__ == "__main__":
    SELECTED_EXPERIMENT = Experiment.DRAFT_ZERO

    interface = WifiInterface.WLP1S0
    ssid = [SSIDs.VU_CAMPUSNET, SSIDs.EDUROAM, SSIDs.IOTROAM]
    
    match SELECTED_EXPERIMENT:
        case Experiment.SCAN_FLOOR:
            ScanFloor(interface, ssid)
        case Experiment.DRAFT_ZERO:
            ThesisDraftZero()
        case Experiment.DRAFT_ONE:
            ThesisDraftOne(interface, ssid)
