from random import uniform
import time
from pandas import read_excel
from rusty_results import Ok, Err, Result
from src.iw_interpret import Cell
from src.enums import Data, WifiInterface

VU_IF = WifiInterface.WLP1S0
AP_DF = read_excel(Data.AP_MAC)
    
def APsFromScanList(ssids, frequencies, interface = VU_IF) -> Result[list[Cell], str]:
    
    match Scan(interface, frequencies):
        case Ok(cells):
            result = []
            
            for cell in cells:
                if cell.ssid in ssids:
                    result.append(cell)
                    
            if len(result):
                return Ok(result)

            return Err(f"Connection with SSIDs {ssids} not found")
        
        case Err(e):
            return Err(e)        

def Scan(interface = VU_IF, frequencies = []) -> Result[list[Cell], str]:
    cell_list = []
    
    try:
        cell_map = Cell.all(interface, frequencies)
        
        for cell in cell_map:
            cell.address = cell.address.lower()
            cell_list.append(cell)       
        
        return Ok(cell_list)
    
    except Exception as e:
        #TODO: error handling
        print(e)
        return Err(str(e))
    
def FindNames(cells: list[Cell]) -> list[Cell]:
    for cell in cells:
        address = cell.address[:-1]+"0"
        in_excel = AP_DF["Base Radio MAC Address"].eq(address).any()

        if in_excel:
            query = "`Base Radio MAC Address` == @address"
            name = AP_DF.query(query)["AP Name"].item()
            cell.name = name
        else:
            cell.name = ''
    
    return cells

def FilterAPs(cells: list[Cell]) -> tuple[list[Cell], list[Cell]]:
    excel_aps = []
    other_aps = []
    cell_index = 0
    
    for cell in cells:
        address = cell.address[:-1]+"0"
        in_excel = AP_DF['Base Radio MAC Address'].eq(address).any()
        
        if in_excel:
            query = "`Base Radio MAC Address` == @address"
            name = AP_DF.query(query)["AP Name"].item()
            cell.name = name
            excel_aps.append(cell)
        else:
            other_aps.append(cell)
            
        cell_index += 1      
    
    return excel_aps, other_aps
        
def FindAPs(ssids, frequencies, interface, min_aps = -1) -> tuple[list[Cell], list[Cell]]:
   
    cell_list = APsFromScanList(ssids, frequencies, interface)
    excel_aps = []
    other_aps = []
    
    match cell_list:
        
        case Err(_e):
            #TODO: error handling
            print(f"ERROR: {_e}")
            return [], []
        
        case Ok(cells):
            
            print('#' * 10)
            excel_aps, other_aps = FilterAPs(cells)
            print(f"Found {len(excel_aps)} (+{len(other_aps)} = {len(excel_aps) + len(other_aps)}):")
            print(excel_aps)
            
    while len(excel_aps) < min_aps:
        duration = uniform(0.1, 0.5)
        time.sleep(duration)
        
        cell_list = APsFromScanList(ssids, frequencies, interface)
        match cell_list:
            case Err(e):
                pass
            
            case Ok(cells):
                w_excel_aps, w_other_aps = FilterAPs(cells)
                for ap in w_excel_aps:
                    if ap.name not in map(lambda xap: xap.name, excel_aps):
                        excel_aps.append(ap)
                        print(f"Added: {ap}")
                for ap in w_other_aps:
                    if ap.address not in map(lambda oap: oap.address, other_aps):
                        other_aps.append(ap)
                
    print(f"Found {len(excel_aps)} (+{len(other_aps)} = {len(excel_aps) + len(other_aps)}):")
    print(excel_aps)

    return excel_aps, other_aps