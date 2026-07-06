import math


PATH_FLOOR_5 = [(36.5, 16.5), (45, 56.5), (18, 56.5), (18, 16.5)]
PATH_FLOOR_6 = [(3, 64.5), (3, 44.5), (9, 44.5), (9, 8.5), (41.5, 8.5), (55, 64.5)]


def lerp(a, b, p):
    return (1 - p) * a + p * b   

def distance(a: tuple, b: tuple):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def FindPosition(floor, percentage: float):
    path = []
    if floor == 5:
        path = PATH_FLOOR_5.copy()
        path.append(PATH_FLOOR_5[0])
    else:
        path = PATH_FLOOR_6.copy()
        path.append(PATH_FLOOR_6[0])
    
    # print(path)
    distances: list[float] = []
    full_distance = 0.0
    for i in range(len(path) - 1):
        d = distance(path[i], path[i+1])
        distances.append(d)
        # print(f"distances: {distances}")
        full_distance += d
    
    traveled = full_distance * percentage
    j = 0
    # print(f"percentage: {percentage}")
    while traveled > distances[j] and j < (len(distances) - 1):
        # print(f"traveled: {traveled}")
        traveled -= distances[j]
        j += 1
    percentage_on_line = traveled/distances[j]
    x = lerp(path[j][0], path[j+1][0], percentage_on_line)
    y = lerp(path[j][1], path[j+1][1], percentage_on_line)

    return (x, y)