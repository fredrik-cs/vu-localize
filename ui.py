from enums import Colors

def ColorPrint(string, color):
    print(color + string, Colors.RESET)
    
def PrintCellSimple(cell, index, success):
    color = Colors.OK_GREEN
    if success:
        color = Colors.OK_BLUE
    else:
        color = Colors.FAIL
    
    ColorPrint(f"Cell {index}:", color)
    
    ColorPrint(f"* SSID: {cell.ssid}", color)
    ColorPrint(f"* Address: {cell.address}", color)
    ColorPrint(f"* Signal strength: {cell.signal} dBm", color)

    print("#" * 10)

