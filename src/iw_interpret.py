from random import uniform
import re
import subprocess
import time
from enums import WifiInterface, SSIDs

class Cell:
    
    def __init__(self):
        self.address: str = ""
        self.signal: int = -999
        self.frequency: int = -999
        self.ssid = ""
        self.age = 999999
        self.name: str = ""
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return self.name
       
    @classmethod
    def all(cls, interface: str, freqs: list[int] = []):
        cells_re = re.compile(r'\nBSS ')
        iwlist_scan = ""
        while iwlist_scan == "":
            #Looping here because of an error where resources are busy
            try:
                if freqs:
                    freqs_strs = list(map(str, freqs))
                    # print(interface)
                    # print(freqs)
                    iwlist_scan = subprocess.check_output(
                        ['sudo', '/sbin/iw', 'dev', interface, 'scan', 'freq', *freqs_strs, 'flush'],
                                                            stderr=subprocess.STDOUT)
                else:
                    iwlist_scan = subprocess.check_output(
                        ['sudo', '/sbin/iw', 'dev', interface, 'scan', 'flush'],
                                                            stderr=subprocess.STDOUT)
            except Exception as e:
                print(f"IW_ERROR:{e}")
                duration = uniform(0.1, 0.5)
                duration = 0.001
                time.sleep(duration)
        
        iwlist_scan = iwlist_scan.decode('utf-8')
        parts = cells_re.split(iwlist_scan)[1:]
        cells = map(Cell.from_string, parts)
        
        return cells
       
    @classmethod 
    def from_string(cls, text):
        return extract(text)
    
    @classmethod
    def trigger_scan(cls):
        subprocess.run(
            ['sudo', '/sbin/iw', 'dev', WifiInterface.WLP1S0, 'scan', 'trigger', 'flush']
        )

    @classmethod
    def dump_scan(cls):
        try:
            iwlist_scan = subprocess.run(
                ['sudo', '/sbin/iw', 'dev', WifiInterface.WLP1S0, 'scan', 'dump'],
                        capture_output=True).stdout
            
            pattern = r"(BSS (?:[\da-z]{2}:){5}[\da-z]{2})(?:.*?signal: )(-\d+)(?:\.\d* dBm\\n\\tlast seen: )(\d+ ms ago)(?:.*?)(SSID: [^\\]+)"
            readable_scans = re.findall(pattern, str(iwlist_scan))

            campnet_scan = filter(lambda x: str(x[3]).endswith(SSIDs.VU_CAMPUSNET), readable_scans)
            sorted_scan = sorted(campnet_scan, key=lambda regex_group: int(regex_group[2].split()[0]))
            
            cells = []
            for scan in sorted_scan:
                cell = Cell()
                cell.address = scan[0]
                cell.signal = int(scan[1])
                cell.age = int(scan[2])
                cell.ssid = scan[3]
                cell.frequency = -1 #TODO: grep frequency in pattern


            # OLDEST_IN_MS = 1000
            # shrunk_scan = list(filter(lambda x: int(x[2].split()[0]) <= OLDEST_IN_MS, shrunk_scan))
            # print(shrunk_scan)
            # strengths = map(lambda x: int(x[1].split(".")[0]), campnet_scan)
            
            # for result in results:
            #     print(result)
            # print("func2 succeeded!")
            return (cells)
        except:
            # print("func2 failed!")
            time.sleep(0.05)
            return ([])
        
def extract(text):
    RE_ADDRESS = r'(([0-9a-f]{2}:){5}([0-9a-f]{2}))'
    RE_FREQUENCY = r'(?:freq: )(\d+)'
    RE_SIGNAL = r'(?:signal: )([-\d\.]+)'
    RE_SSID = r'(?:SSID: )(\S+)'
    
    lines = text.split("\n")
    cell = Cell()
    
    for line in lines:
        address_match = re.search(RE_ADDRESS, line)
        if address_match:
            cell.address = address_match.group(1)
            continue
        
        frequency_match = re.search(RE_FREQUENCY, line)
        if frequency_match:
            cell.frequency = int(frequency_match.group(1))
            continue
        
        signal_match = re.search(RE_SIGNAL, line)
        if signal_match:
            cell.signal = int(signal_match.group(1))
            continue
        
        ssid_match = re.search(RE_SSID, line)
        if ssid_match:
            cell.ssid = ssid_match.group(1)
            continue
    
    return cell
    
    
if __name__ == "__main__":
    interface = "wlp1s0"
    
    # cells = Cell.all(interface)
    cells = Cell.all(interface, [2412, 2437, 5200])
    
    for cell in cells:
        print("-------------------")
        print(cell.address)
        print(cell.frequency)
        print(cell.ssid)
        print(cell.signal)