from pandas import read_excel
from enums import Data, WifiInterface
from result import Ok, Err, Result
from iw_interpret import Cell

from ui import PrintCellSimple

VU_IF = WifiInterface.WLAN0
    
def FindFromScanList(ssid, frequencies, interface = VU_IF) -> Result[list[Cell], str]:
    
    match Scan(interface, frequencies):
        case Ok(cells):
            result = []
            
            for cell in cells:
                if cell.ssid == ssid:
                    result.append(cell)
                    
            if len(result):
                return Ok(result)

            return Err(f"Connection with SSID {ssid} not found")
        
        case Err(e):
            return Err(e)

def Scan(interface = VU_IF, frequencies = []) -> Result[list[Cell], str]:
    cell_list = []
    
    try:
        cell_map = Cell.all(interface)
        
        for cell in cell_map:
            cell.address = cell.address.lower()
            cell_list.append(cell)       
        
        return Ok(cell_list)
    
    except Exception as e:
        print("oh no!")
        return Err(e)
    
def FindAPs(ssid, interface, frequencies) -> tuple[list[Cell], list[Cell]]:
    cell_index = 0
    excel_aps = []
    excel_aps_names = []
    other_aps = []
    cell_list = FindFromScanList(ssid, interface, frequencies)
    # cell_list = Scan(interface)
    
    match cell_list:
        
        case Ok(cells):
            df = read_excel(Data.AP_MAC)
            print('#' * 10)
            
            for cell in cells:
                cell_index += 1
                address = cell.address
                in_excel = df['Base Radio MAC Address'].eq(address).any()
                
                if in_excel:
                    query = "`Base Radio MAC Address` == @address"
                    name = df.query(query)["AP Name"].item()
                    # print(f"Found! {name}")
                    cell.name = name
                    excel_aps.append(cell)
                    excel_aps_names.append(name)
                else:
                    other_aps.append(cell)
                    
                # PrintCellSimple(cell, cell_index, in_excel)
            
            print(f"Found {len(excel_aps)} (+{cell_index - len(excel_aps)} = {cell_index}):")
            print(excel_aps_names)
            return excel_aps, other_aps
        
        case Err(_e):
            print(_e)
            print("not this!")
            return [], []