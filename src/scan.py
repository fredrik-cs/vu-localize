from random import uniform
import time
from pandas import read_excel
from result import Ok, Err, Result
from src.iw_interpret import Cell
from src.ui import PrintCellSimple
from src.enums import Data, WifiInterface

VU_IF = WifiInterface.WLP1S0
AP_DF = read_excel(Data.AP_MAC)
    
def APsFromScanList(ssid, frequencies, interface = VU_IF) -> Result[list[Cell], str]:
    
    match Scan(interface, frequencies):
        case Ok(cells):
            result = []
            
            for cell in cells:
                if cell.ssid == ssid:
                    result.append(cell)
                    
            if len(result):
                # print(result)
                return Ok(result)

            return Err(f"Connection with SSID {ssid} not found")
        
        case Err(e):
            return Err(e)

# def FindAtleastMinScans(ssid, frequencies, min = 3) -> Result[list[Cell], None]:
#     result = []
#     addresses = []
    
#     while len(result) < min:
#         match FindFromScanList(ssid, frequencies):
#             case Ok(cells):
#                 for cell in cells:
#                     if cell.address not in addresses:
#                         addresses.append(cell.address)
#                         result.append(cell)
#             case Err(_):
#                 pass
    
#     return Ok(result)
            

def Scan(interface = VU_IF, frequencies = []) -> Result[list[Cell], str]:
    cell_list = []
    
    try:
        cell_map = Cell.all(interface, frequencies)
        # print(cell_map)
        
        for cell in cell_map:
            cell.address = cell.address.lower()
            cell_list.append(cell)       
        
        # print(cell_list)
        return Ok(cell_list)
    
    except Exception as e:
        #TODO: error handling
        return Err(e)
    
def FilterAPs(cells) -> tuple[list[Cell], list[Cell]]:
    excel_aps = []
    other_aps = []
    
    for cell in cells:
        address = cell.address
        in_excel = AP_DF['Base Radio MAC Address'].eq(address).any()
        
        if in_excel:
            query = "`Base Radio MAC Address` == @address"
            name = AP_DF.query(query)["AP Name"].item()
            # print(f"Found! {name}")
            cell.name = name
            excel_aps.append(cell)
            # excel_aps_names.append(name)
        else:
            other_aps.append(cell)
            
        # PrintCellSimple(cell, cell_index, in_excel)    
        return excel_aps, other_aps
        
def FindAPs(ssid, frequencies, interface, min_aps = -1) -> tuple[list[Cell], list[Cell]]:
   
    cell_list = APsFromScanList(ssid, frequencies, interface)
    # cell_list = FindAtleastMinScans(ssid, interface, 3)
    # cell_list = Scan(interface)
    
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
        
        cell_list = APsFromScanList(ssid, frequencies, interface)
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