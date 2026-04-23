import re

from enums import Data


def GetUnityCoordinates(selected_floor) -> list:
    lines = []
    unity_coordinates = []

    x_scale = 24.2
    x_bias = 25.0
    z_scale = -24.2
    z_bias = 1785.0
    
    with open(Data.UNITY_COORDS_ON_FLOOR.format(selected_floor)) as f:
        lines = f.readlines()
    
    coordinate_pattern = r'([0-9]*),([0-9]*);([0-9\.]*),([0-9\.]*),([0-9\.]*)'
    
    for line in lines:
        coord_line = re.match(coordinate_pattern, line)
        if coord_line:
            x = float(coord_line.group(3)) * x_scale + x_bias
            z = float(coord_line.group(5)) * z_scale + z_bias
            
            unity_coordinates.append((x, z))
            
    return unity_coordinates

def APCoordinates():
    lines = []
    coordinates = []
    floor = 5
    
    x_scale = 24.2
    x_bias = 25.0
    z_scale = -24.2
    z_bias = 1785.0
    
    with open(Data.COORDS_OF_APS) as f:
        lines = f.readlines()
        
    def APOnFloor(line):
        return line[6] == str(floor)
        
    lines = list(
                filter(APOnFloor, lines)
            )
        
    coordinate_pattern = r'([A-Z\-]*[0-9]*)(?: -> )([0-9\.]*),([0-9\.]*),([0-9\.]*)'
    
    for line in lines:
        coord_line = re.match(coordinate_pattern, line)
        if coord_line:
            x = float(coord_line.group(2)) * x_scale + x_bias
            z = float(coord_line.group(4)) * z_scale + z_bias
            coordinates.append((x, z))
    
    return coordinates

if __name__ == "__main__":
    import matplotlib as mpimg
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    cwd = os.getcwd()
    print(cwd)

    image = plt.imread("map floor five.jpg")
    ap_pts = np.array(APCoordinates())
    unitycoords = GetUnityCoordinates(5)
    un_pts = np.array(unitycoords)

    plt.imshow(image)
    plt.scatter(ap_pts[:, 0], ap_pts[:, 1], marker="o", color="green", s=5)
    plt.scatter(un_pts[:, 0], un_pts[:, 1], marker="o", color="purple", s=5)
    plt.show()