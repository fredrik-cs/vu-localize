import re
import subprocess
import time

class Cell:
    
    def __init__(self):
        self.address = None
        self.signal = None
        self.frequency = None
        self.ssid = None
       
    @classmethod
    def all(cls, interface: str, freqs: list[int] = []):
        cells_re = re.compile(r'\nBSS ')
        iwlist_scan = ""
        while iwlist_scan == "":
            #Looping here because of an error where resources are busy
            try:
                if freqs:
                    freqs = list(map(str, freqs))
                    print(freqs)
                    iwlist_scan = subprocess.check_output(
                        ['sudo', '/sbin/iw', 'dev', interface, 'scan', 'freq', *freqs, 'flush'],
                                                            stderr=subprocess.STDOUT)
                else:
                    iwlist_scan = subprocess.check_output(
                        ['sudo', '/sbin/iw', 'dev', interface, 'scan', 'flush'],
                                                            stderr=subprocess.STDOUT)
            except Exception as e:
                time.sleep(.1)
        
        iwlist_scan = iwlist_scan.decode('utf-8')
        parts = cells_re.split(iwlist_scan)[1:]
        cells = map(Cell.from_string, parts)
        
        return cells
       
    @classmethod 
    def from_string(cls, text):
        return extract(text)
        
        
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
            cell.frequency = frequency_match.group(1)
            continue
        
        signal_match = re.search(RE_SIGNAL, line)
        if signal_match:
            cell.signal = signal_match.group(1)
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