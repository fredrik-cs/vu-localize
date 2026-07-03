import math


PATH_FLOOR_5 = []
PATH_FLOOR_6 = []


def lerp(a, b, p):
    return (1 - p) * a + p * b   

def distance(a: tuple, b: tuple):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def FindPosition(floor, percentage):
    path = []
    if floor == 5:
        path = PATH_FLOOR_5 + PATH_FLOOR_5[0]
    else:
        path = PATH_FLOOR_6 + PATH_FLOOR_6[0]

    distances = []
    full_distance = 0
    for i in range(len(path) - 1):
        d = distance(path[i], path[i+1])
        distances.append(d)
        full_distance += d
    
    traveled = full_distance * percentage
    j = 0
    while traveled > distances[j]:
        traveled -= distances[j]
        j += 1
    percentage_on_line = traveled/distances[j]
    x = math.lerp(path[j][0], path[j+1][0], percentage_on_line)
    y = math.lerp(path[j][1], path[j+1][1], percentage_on_line)

    return (x, y)