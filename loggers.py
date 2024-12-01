import re
from iw_interpret import Cell
from functools import partial
from enums import Log

def Logger(regex_pattern, log_uri):
    def _InnerDecorator(function):
        def FunctionWrapped(*args, **kwargs):
            log_lines = []
            matches = []
            log = ""
    
            with open(log_uri) as f:
                log_lines = f.readlines()
                f.close()
            
            for line in log_lines:
                found_match = re.search(regex_pattern, line)
                if found_match:
                    matches.append(found_match)
            
            partial_function = partial(function, lines=log_lines, matches=matches)
            function_lines, log_lines = partial_function(*args)
            
            for line in function_lines:
                log += line
            
            for line in log_lines:
                log += line
                
            with open(log_uri, "w") as f:
                f.write(log)
                f.close()
        
        return FunctionWrapped
    return _InnerDecorator
     
# -----------------------------------------     
#     
# Loggers start here
# All need the @Logger decorator and a (tail-end) lines and matches argument
#
# ----------------------------------------- 
     
@Logger(
    regex_pattern = r'(?:-> )([:A-Za-z0-9]+)',
    log_uri = Log.UNKNOWN_APS
)
def LogUnknowns(unknowns: list[Cell], lines: list[str], matches: list[re.Match[str]]):
    log = []
    addresses = []
    
    for match in matches:
        addresses.append(match.group(1))
    
    for cell in unknowns:
        if cell.address not in addresses:
            log.append("{ssid:<32} -> {address}\n"
                .format(ssid=cell.ssid, address= cell.address))
            
    return log, lines

@Logger(
    regex_pattern = r'(\S*)(?: -> )([0-9]\.[0-9]+ GHz)',
    log_uri = Log.FREQUENCIES
)
def LogFrequencies(cells: list[Cell], lines:list[str], matches: list[re.Match[str]]):
    log = []
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
            
            log.append("{address:<17} -> {name:<10} -> {frequency}\n"
                .format(name=cell.name, address=cell.address, frequency=cell_frequency))
            
    return log, lines
    
