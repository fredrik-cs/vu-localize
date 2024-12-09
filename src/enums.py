class WifiInterface:
    WLAN0 = 'wlan0'
    WLP1S0 = 'wlp1s0'
    
class SSIDs:
    VU_CAMPUSNET = 'VU-Campusnet'
    EDUROAM = 'eduroam'

class Band:
    G2_4 = [2412, 2437, 2462]
    G5 = [5180, 5200, 5220, 5240, 5260, 5280, 5300, 5320, 5500, 5520, 5560, 5580]
    BOTH = [2412, 2437, 2462, 5180, 5200, 5220, 5240, 5260, 5280, 5300, 5320, 5500, 5520, 5560, 5580]
    ALL = []
    
class Data:
    AP_MAC = 'data/NU-AP-MAC.xlsx'
    BUILDING_COORDS = 'data/samplesF5-multilayer.csv'
    INTEGER_COORDS_ON_FLOOR = 'data/coordinates_f{}_extended.txt'
    UNITY_COORDS_ON_FLOOR = 'data/coordinates_f{}_extended.txt'
    COORDS_OF_APS = 'data/ap_coordinates.txt'
    
class Log:
    UNKNOWN_APS = 'log/unknowns.log'
    FREQUENCIES = 'log/frequencies.log'
    
class Colors:
    RESET = '\033[0m'
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
