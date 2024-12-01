import math
import re
import pandas as pd
from itertools import islice

from enums import Data

class UnityCoordinate:
    def __init__(self, x, y, z):
        self.x: float = x
        self.y: float = y
        self.z: float = z
    
    def distance(self, other):
        self.x = float(self.x)
        other.x = float(other.x)
        self.y = float(self.y)
        other.y = float(other.y)
        self.z = float(self.z)
        other.z = float(other.z)
        
        d = math.sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2) + pow(self.z - other.z, 2))
        return UnityToMeter(d)
    
    def __str__(self):
        return '({x:<8},{y:^8},{z:>8})'.format(
            x = self.x,
            y = self.y,
            z = self.z,
        )
    def __repr__(self):
        return self.__str__()

class Coordinate:
    def __init__(self, floor, x, y):
        self.floor = floor
        self.x: int = x
        self.y: int = y
        
    def __str__(self):
        return 'Floor {floor}: ({x:>2}, {y:<2})'.format(
            floor=self.floor, 
            x=self.x, 
            y=self.y)
        
    def __repr__(self):
        return self.__str__()
 
def UnityToMeter(x):
    # TODO: Meassure more precisely. 5 is a rough estimate.
    return float(x) / 5.0 

def MeterToUnity(x):
    # TODO: Meassure more precisely. 5 is a rough estimate.
    return float(x) * 5.0  
            
def GetCoordinates(selected_floor) -> list[Coordinate]:
    lines = []
    coordinates = []
    
    with open(Data.INTEGER_COORDS_ON_FLOOR.format(selected_floor)) as f:
        lines = f.readlines()
    
    coordinate_pattern = r'([0-9]*):([0-9]*),([0-9]*);([0-9\.]*),([0-9\.]*),([0-9\.]*)'
    
    for line in lines:
        coord_line = re.match(coordinate_pattern, line)
        if coord_line:
            floor = coord_line.group(1)
            x = coord_line.group(2)
            y = coord_line.group(3)
            
            coordinates.append(Coordinate(floor, x, y))
            
    return coordinates

def GetUnityCoordinates(selected_floor) -> list[UnityCoordinate]:
    lines = []
    unity_coordinates = []
    
    with open(Data.UNITY_COORDS_ON_FLOOR.format(selected_floor)) as f:
        lines = f.readlines()
    
    coordinate_pattern = r'([0-9]*):([0-9]*),([0-9]*);([0-9\.]*),([0-9\.]*),([0-9\.]*)'
    
    for line in lines:
        coord_line = re.match(coordinate_pattern, line)
        if coord_line:
            x = float(coord_line.group(4))
            y = float(coord_line.group(5))
            z = float(coord_line.group(6))
            
            unity_coordinates.append(UnityCoordinate(x, y, z))
            
    return unity_coordinates

def GetAPUnityCoordinates(cells):
    lines = []
    coordinates = []
    
    with open(Data.COORDS_OF_APS) as f:
        lines = f.readlines()
        
    def APInCells(line, cells):
        for cell in cells:
            if cell.name == line[:10]:
                cell.coord = line
                return True
        return False
        
    lines = list(
                filter(lambda line: APInCells(line, cells), lines)
            )
        
    coordinate_pattern = r'([A-Z\-]*[0-9]*)(?: -> )([0-9\.]*),([0-9\.]*),([0-9\.]*)'
    
    for cell in cells:
        coord_line = re.match(coordinate_pattern, cell.coord)
        if coord_line:
            x = float(coord_line.group(2))
            y = float(coord_line.group(3))
            z = float(coord_line.group(4))
            cell.coords = UnityCoordinate(x, y, z)
            # coordinates.append(UnityCoordinate(x, y, z))

    # return coordinates

def MakeAPCoordinatesList():
    df = pd.read_csv(Data.BUILDING_COORDS)
    columns = df.columns.to_list()
    filtered_columns = list(filter(lambda name: len(name) == 12, columns))
    
    def Chunk(it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())
    
    chunked_columns = list(Chunk(filtered_columns,3))
    print(chunked_columns)
    
    log = ""
    for chunk in chunked_columns:
        name = chunk[0].removesuffix("_x")
        x = df[chunk[0]].iloc[0]
        y = df[chunk[1]].iloc[0]
        z = df[chunk[2]].iloc[0]
        log += "{name:<10} -> {x},{y},{z}\n".format(name=name, x=x, y=y, z=z)
    
    print(log)
    with open(Data.COORDS_OF_APS, "w") as f:
        f.write(log)
        f.close()