import re
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import numpy as np
import os

from src.enums import Data

def PlotPointsOnFloor(points, floor):
    # print(f"points: {points}")

    x_scale = 24.2
    x_bias = 25.0
    z_scale = -24.2
    z_bias = 1785.0

    points["ml"] = list(map(lambda x : (x[0] * x_scale + x_bias, x[1] * z_scale + z_bias), points["ml"]))

    ml_pts = np.array(points["ml"])
    tl_pts = np.array(points["tl"])
    mb_pts = np.array(points["mb"])
    mbf_pts = np.array(points["mbf"]) 
    ml_steps = np.linspace(0,1,len(points["ml"]))
    tl_steps = np.linspace(0,1,len(points["tl"]))
    mb_steps = np.linspace(0,1,len(points["mb"]))
    mbf_steps = np.linspace(0,1,len(points["mbf"]))

    image = ''
    if floor == 5:
        image = 'map floor five.jpg'
    else:
        image = 'map floor six.jpg'

    # f = plt.figure()    
    # f, axes = plt.subplots(nrows = 2, ncols = 2)

    

    cwd = os.getcwd()
    print(cwd)

    image = plt.imread(image)
    plt.imshow(image)
    plt.scatter(ml_pts[:, 0], ml_pts[:, 1], marker='x', c=ml_steps, cmap = 'hsv', s=10)
    # if ml_pts.any(): 
    #     axes[0][0].scatter(ml_pts[:, 0], ml_pts[:, 1], marker='o', c=ml_steps, cmap="hsv", s=5)
    #     axes[0][0].set_xlabel('ML: Circles', labelpad = 5)
    # if tl_pts.any(): 
    #     axes[0][1].scatter(tl_pts[:, 0], tl_pts[:, 1], marker='x', c=tl_steps, cmap="hsv", s=5)
    #     axes[0][1].set_xlabel('TL: Crosses', labelpad = 5)
    # if mb_pts.any(): 
    #     axes[1][0].scatter(mb_pts[:, 0], mb_pts[:, 1], marker='*', c=mb_steps, cmap="hsv", s=5)
    #     axes[1][0].set_xlabel('MB: Stars', labelpad = 5)
    # if mbf_pts.any(): 
    #     axes[1][1].scatter(mbf_pts[:, 0], mbf_pts[:, 1], marker='s', c=mbf_steps, cmap="hsv", s=5)
    #     axes[1][1].set_xlabel('MBF: Squares', labelpad = 5)
    plt.show()
    

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

    # cwd = os.getcwd()
    # print(cwd)

    image = plt.imread("map floor five.jpg")
    ap_pts = np.array(APCoordinates())
    unitycoords = GetUnityCoordinates(5)
    un_pts = np.array(unitycoords)

    plt.imshow(image)
    plt.scatter(ap_pts[:, 0], ap_pts[:, 1], marker="o", color="green", s=5)
    plt.scatter(un_pts[:, 0], un_pts[:, 1], marker="o", color="purple", s=5)
    plt.show()