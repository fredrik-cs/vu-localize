from random import uniform
import re
import subprocess
import sys
import time
from src.enums import WifiInterface

VU_IF = WifiInterface.WLP2S0

class Cell:
    
    def __init__(self):
        self.address: str = ""
        self.signal: int = -999
        self.frequency: int = -999
        self.ssid: str = ""
        self.age: int = 999999
        self.name: str = ""
        self.distance: int = -999
        self.coord_transform = ""
        self.coords: tuple = (None, None, None)
        self.timestamp: int = sys.maxsize
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"{self.ssid}: {self.signal} dBm at {self.frequency} Mhz"
       
    @classmethod
    def all(cls, interface: str, freqs: list[int] = []):
        cells_re = re.compile(r'\nBSS ')
        iwlist_scan = ""
        while iwlist_scan == "":
            #Looping here because of an error where resources are busy
            try:
                if freqs:
                    freqs_strs = list(map(str, freqs))
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
    def trigger_scan(cls, freqs = []):
    
        if freqs:
            frequencies = list(map(lambda x: str(x), freqs))
            subprocess.run(
                ['sudo', '/sbin/iw', 'dev', VU_IF, 'scan', 'trigger', 'freq', *frequencies, 'flush'],
                stdout=subprocess.PIPE, stderr= subprocess.DEVNULL
                )

        else:
            subprocess.run(
                ['sudo', '/sbin/iw', 'dev', VU_IF, 'scan', 'trigger', 'flush'],
                stdout=subprocess.PIPE, stderr= subprocess.DEVNULL
                )

    @classmethod
    def _dump(cls):
        iwlist_scan = subprocess.run(
                ['sudo', '/sbin/iw', 'dev', VU_IF, 'scan', 'dump'],
                        capture_output=True).stdout
        return iwlist_scan

    @classmethod
    def dump_scan(cls):
        try:
            iwlist_scan = Cell._dump()
            
            pattern = r"(?:BSS )((?:[\da-z]{2}:){5}[\da-z]{2})(?:.*?freq: )(\d*)(?:.*?signal: )(-\d+)(?:.*?last seen: )(\d+)(?:.*?SSID: )([^\\]+)"
            readable_scans = re.findall(pattern, str(iwlist_scan))
        

            # campnet_scan = filter(lambda x: str(x[4]).endswith(SSIDs.VU_CAMPUSNET), readable_scans)
            sorted_scan = sorted(readable_scans, key=lambda regex_group: int(regex_group[3]))

            cells: list[Cell] = []
            for scan in sorted_scan:
                cell = Cell()
                cell.address = scan[0]
                cell.frequency = int(scan[1])
                cell.signal = int(scan[2])
                cell.age = int(scan[3])
                cell.ssid = scan[4]
                cells.append(cell)
            return (cells)
        except:
            print("dump failed!")
            time.sleep(0.05)
            empty: list[Cell] = []
            return (empty)
        
def extract(text):
    RE_ADDRESS = r'(([0-9a-f]{2}:){5}([0-9a-f]{2}))'
    RE_FREQUENCY = r'(?:freq: )(\d+)'
    RE_SIGNAL = r'(?:signal: )([-\d]+)'
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
    
    