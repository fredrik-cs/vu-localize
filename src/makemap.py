import re
import matplotlib.pyplot as plt
import numpy as np
import os

from src.enums import Data, Maps

X_SCALE = 24.2
X_BIAS = 25.0
Z_SCALE = -24.2
Z_BIAS = 1785.0

def PlotPathOnFloor(path: list[tuple[int, int]], floor):
    points = list(map(lambda x : (x[0] * X_SCALE + X_BIAS, x[1] * Z_SCALE + Z_BIAS), path))
    point_count = len(points)
    points.append(points[0])
    pts = np.array(points)
    print(pts)

    image = ''
    if int(floor) == 5:
        image = Maps.FLOOR5
    else:
        image = Maps.FLOOR6
    
    fig, ax = plt.subplots(1)
    image = plt.imread(image)
    ax.set_aspect('equal')
    ax.imshow(image)

    for i in range(point_count):
        xline = [pts[i, 0], pts[i+1, 0]]
        yline = [pts[i, 1], pts[i+1, 1]]
        plt.plot(xline, yline, c="orange")

    plt.show()


def PlotErrorOnFloor(coordinates, distances, floor, prediction = []):
    points = list(map(lambda x : (x[0] * X_SCALE + X_BIAS, x[2] * Z_SCALE + Z_BIAS), coordinates))
    pts = np.array(points)
    print(pts)

    image = ''
    if int(floor) == 5:
        image = Maps.FLOOR5
    else:
        image = Maps.FLOOR6
    
    fig, ax = plt.subplots(1)
    image = plt.imread(image)
    ax.set_aspect('equal')
    ax.imshow(image)
        
    plt.scatter(pts[:, 0], pts[:, 1], marker='x', c='green', s=10)
    circles = [plt.Circle((x, y), r*X_SCALE, edgecolor='red', facecolor='none') for (x,y,r) in zip(pts[:, 0], pts[:, 1], distances)]
    # x1 = [pts[1, 0], pts[1, 0] - (distances[1] * X_SCALE)]
    # y1 = [pts[1, 1], pts[1, 1]]
    # print(x1, y1)
    # plt.plot(x1, y1, c="orange")
    for circle in circles:
        ax.add_patch(circle)
    if prediction:
        print(prediction)
        prediction = [prediction[0] * X_SCALE + X_BIAS, prediction[2] * Z_SCALE + Z_BIAS]
        print(prediction)
        plt.scatter(prediction[0], prediction[1], marker='x', c='purple', s=20)
    plt.show()

    

def PlotPointsOnFloor(points, floor):
    # print(f"points: {points}")

    points = list(map(lambda x : (x[0] * X_SCALE + X_BIAS, x[1] * Z_SCALE + Z_BIAS), points))

    ml_pts = np.array(points)
    ml_steps = np.linspace(0,1,len(points))

    image = ''
    if floor == 5:
        image = Maps.FLOOR5
    else:
        image = Maps.FLOOR6

    cwd = os.getcwd()
    print(cwd)

    image = plt.imread(image)
    plt.imshow(image)
    plt.scatter(ml_pts[:, 0], ml_pts[:, 1], marker='x', c=ml_steps, cmap = 'hsv', s=10)
    plt.show()
    

def GetUnityCoordinates(selected_floor) -> list:
    lines = []
    unity_coordinates = []
    
    with open(Data.UNITY_COORDS_ON_FLOOR.format(selected_floor)) as f:
        lines = f.readlines()
    
    coordinate_pattern = r'([0-9]*),([0-9]*);([0-9\.]*),([0-9\.]*),([0-9\.]*)'
    
    for line in lines:
        coord_line = re.match(coordinate_pattern, line)
        if coord_line:
            x = float(coord_line.group(3)) * X_SCALE + X_BIAS
            z = float(coord_line.group(5)) * Z_SCALE + Z_BIAS
            
            unity_coordinates.append((x, z))
            
    return unity_coordinates

def APCoordinates():
    lines = []
    coordinates = []
    floor = 5
    
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
            x = float(coord_line.group(2)) * X_SCALE + X_BIAS
            z = float(coord_line.group(4)) * Z_SCALE + Z_BIAS
            coordinates.append((x, z))
    
    return coordinates


if __name__ == "__main__":
    image = plt.imread(Maps.FLOOR5)
    ap_pts = np.array(APCoordinates())
    unitycoords = GetUnityCoordinates(5)
    un_pts = np.array(unitycoords)

    plt.imshow(image)
    plt.scatter(ap_pts[:, 0], ap_pts[:, 1], marker="o", color="green", s=5)
    plt.scatter(un_pts[:, 0], un_pts[:, 1], marker="o", color="purple", s=5)
    plt.show()