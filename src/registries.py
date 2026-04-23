import re
from functools import partial
from src.enums import Log
from src.iw_interpret import Cell

def Registry(regex_pattern, register_uri):
    def _InnerDecorator(function):
        def FunctionWrapped(*args, **kwargs):
            register_lines = []
            matches = []
            register = ""
    
            with open(register_uri) as f:
                register_lines = f.readlines()
                f.close()
            
            for line in register_lines:
                found_match = re.search(regex_pattern, line)
                if found_match:
                    matches.append(found_match)
            
            partial_function = partial(function, lines=register_lines, matches=matches)
            function_lines, register_lines = partial_function(*args)
            
            for line in function_lines:
                register += line
            
            for line in register_lines:
                register += line
                
            with open(register_uri, "w") as f:
                f.write(register)
                f.close()
        
        return FunctionWrapped
    return _InnerDecorator
     
# -----------------------------------------     
#     
# Registries start here
# All need the @Registry decorator and a (tail-end) lines and matches argument
#
# ----------------------------------------- 
     
@Registry(
    regex_pattern = r'(?:-> )([:A-Za-z0-9]+)',
    register_uri = Log.UNKNOWN_APS
)
def RegisterUnknowns(unknowns: list[Cell], lines: list[str], matches: list[re.Match[str]]):
    register = []
    addresses = []
    
    for match in matches:
        addresses.append(match.group(1))
    
    for cell in unknowns:
        if cell.address not in addresses:
            register.append("{ssid:<32} -> {address}\n"
                .format(ssid=cell.ssid, address= cell.address))
            
    return register, lines

@Registry(
    regex_pattern = r'(\S*)(?: -> )([0-9]\.[0-9]+ GHz)',
    register_uri = Log.FREQUENCIES
)
def RegisterFrequencies(cells: list[Cell], lines:list[str], matches: list[re.Match[str]]):
    # TODO: Fix duplicates
    register = []
    name_to_frequencies = {}
    
    for match in matches:
        matched_name = match.group(1)
        frequency = match.group(2)
        frequency = str(frequency)
        frequency = frequency[0] + '.' + frequency[1:] + " GHz"
        
        if matched_name not in name_to_frequencies:
            name_to_frequencies[matched_name] = [frequency]
        else:
            name_to_frequencies[matched_name].append(frequency)
    
    for cell in cells:
        if ((cell.name not in name_to_frequencies) or (cell.frequency not in name_to_frequencies[cell.name])):
            cell_frequency = "{thousands}.{decimal:0>3} GHz".format(
                thousands = int(cell.frequency) // 1000, decimal = int(cell.frequency) % 1000)
            
            register.append("{address:<17} -> {name:<10} -> {frequency}\n"
                .format(name=cell.name, address=cell.address, frequency=cell_frequency))
            
    return register, lines
    
