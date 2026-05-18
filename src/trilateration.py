import math
import numpy as np
from src.coordinates import MeterToUnity, UnityCoordinate, UnityToMeter

#https://iotandelectronics.wordpress.com/2016/10/07/how-to-calculate-distance-from-the-rssi-value-of-the-ble-beacon/
def AnalyticalDistanceToAP(power, base_power = -47.0, environmental_factor = 4.0):
    ### power = measured signal right now
    ### base_power = signal strength at 1 meter. 
    #   -47 is measured from one AP, but different APs could have different base powers.
    #   could look into effect of specifying base power for known APs
    ### environmental factor = a factor between 2 and 4
    ### 2 means lower power = big increase in distance, 4 means lower power = smaller increase in distance
    power = float(power)
    return 10.0 ** ((base_power - power)/(10.0 * environmental_factor))
#10.0 ^ ((-47 - (-67))/(10 * 4)) 

#TODO: AnalyticalDistanceToAP might not be the best solution for indoor estimates. Try find alternative and good explanation as to why which is better.
#def DistanceToAP(signal_strength, frequency_in_MHz)

def Trilaterate2D(coords_A, coords_B, coords_C, distance_A, distance_B, distance_C):
    A = pow(coords_A.x, 2) + pow(coords_A.y, 2) - pow(distance_A, 2)
    B = pow(coords_B.x, 2) + pow(coords_B.y, 2) - pow(distance_B, 2)
    C = pow(coords_C.x, 2) + pow(coords_C.y, 2) - pow(distance_C, 2)
    X13 = coords_A.x - coords_C.x
    X21 = coords_B.x - coords_A.x
    X32 = coords_C.x - coords_B.x
    Y13 = coords_A.y - coords_C.y
    Y21 = coords_B.y - coords_A.y
    Y32 = coords_C.y - coords_B.y
    x = (A*Y32 + B*Y13 + C*Y21)/(2*(coords_A.x*Y32 + coords_B.x*Y13 + coords_C.x*Y21)) 
    y = (A*X32 + B*X13 + C*X21)/(2*(coords_A.x*X32 + coords_B.x*X13 + coords_C.x*X21))
    return UnityCoordinate(x, y, None)

def Trilaterate3D(cA, cB, cC, dA, dB, dC):
    #cX = coordinate X
    #dX = distance to X from unknown coordinate

    def sqr(x):
        return pow(x, 2)
    
    cAx = UnityToMeter(cA.x)
    cAy = UnityToMeter(cA.y)
    cAz = UnityToMeter(cA.z)
    
    cBx = UnityToMeter(cB.x)
    cBy = UnityToMeter(cB.y)
    cBz = UnityToMeter(cB.z)
    
    cCx = UnityToMeter(cC.x)
    cCy = UnityToMeter(cC.y)
    cCz = UnityToMeter(cC.z)
    
    dA = float(dA)
    dB = float(dB)
    dC = float(dC)
    
    A = -2.0 * (cAx - cBx)  
    B = -2.0 * (cAy - cBy) 
    C = -2.0 * (cAz - cBz)
    D = float(sqr(dA) + sqr(cBx) + sqr(cBy) + sqr(cBz) - sqr(dB) - sqr(cAx) - sqr(cAy) - sqr(cAz))
    
    E = -2.0 * (cBx - cCx)  
    F = -2.0 * (cBy - cCy) 
    G = -2.0 * (cBz - cCz)
    H = float(sqr(dB) + sqr(cCx) + sqr(cCy) + sqr(cCz) - sqr(dC) - sqr(cBx) - sqr(cBy) - sqr(cBz))
    
    I = -2.0 * (cCx - cAx)  
    J = -2.0 * (cCy - cAy) 
    K = -2.0 * (cCz - cAz)
    L = float(sqr(dC) + sqr(cAx) + sqr(cAy) + sqr(cAz) - sqr(dA) - sqr(cCx) - sqr(cCy) - sqr(cCz))
    
    M = (A*F*K) - (A*G*J) - (B*E*K) + (B*G*I) + (C*E*J) - (C*F*I) # A(FK-GJ) + B(GI-EK) + C(EJ-FI) | E(CJ-BK) + F(AK - CI) + G(BI - AJ) | I(BG - CF) + J(CE - FI) + K(AF - BE)
    M1 = (D*F*K) - (D*G*J) - (B*H*K) + (B*G*L) + (C*H*J) - (C*F*L)
    M2 = (A*H*K) - (A*G*L) - (D*E*K) + (D*G*I) + (C*E*L) - (C*H*I)
    M3 = (A*F*L) - (A*H*J) - (B*E*L) + (B*H*I) + (D*E*J) - (D*F*I)
    
    # Division by M fails if any two coordinates are the same
    x = MeterToUnity(M1/M)
    y = MeterToUnity(M2/M)
    z = MeterToUnity(M3/M)
    
    return UnityCoordinate(x, y, z)

def Trilaterate3DAlternate(cA, cB, cC, dA, dB, dC):
    # https://en.wikipedia.org/wiki/True-range_multilateration#Three_Cartesian_dimensions,_three_measured_slant_ranges
    
    # print(cA, cB, cC, dA, dB, dC)

    cAx = cA.x
    cAy = cA.y
    cAz = cA.z
    
    cBx = cB.x
    cBy = cB.y
    cBz = cB.z
    
    cCx = cC.x
    cCy = cC.y
    cCz = cC.z
    
    
    dA = float(dA)
    dB = float(dB)
    dC = float(dC)
    # print(f"dA = {dA} | dB = {dB} | dC = {dC}")
    # Translate and rotate the problem to an easier to solve space, then rotate and translate back.
    # print(f"A = {(cAx,cAy,cAz)} | B = {cBx,cBy,cBz} | C = {cCx,cCy,cCz}")
    cBx -= cAx
    cBy -= cAy
    cBz -= cAz
    cCx -= cAx
    cCy -= cAy
    cCz -= cAz
    # print(f"A = {(cAx,cAy,cAz)} | B = {cBx,cBy,cBz} | C = {cCx,cCy,cCz}")
    #cA = 0, but keep same for later

    # TODO: cannot handle cBz = cAz, cCy = cAy, cBx = cAx

    #Now the rotations. First rotate B around the X-axis to eliminate Y, applying the same rotation to C.
    # Then rotate B around Y to eliminate Z, applying the same for C
    # Now, with A and B locked to the x axis, rotate C around the X-axis to elimate Z
    
    #rotate B around the x axis,
    #but first figure out the angle that you need for a rotation around the x-axis to make y = 0
    #for that ycos(theta) - zsin(theta) = 0
    # zsin(theta) = ycos(theta)
    # sin(theta)/cos(theta) = y/z
    # theta = atan(y/z)
    # so x = x, y = ycos(theta) - zsin(theta) = 0 and z = ysin(theta) + zcos(theta)
    try: 
        x_rot = round(math.atan(cBy/cBz), 2)
        # print(f"x_rot == {x_rot}")
        #cBy == 0?
        # print(f"{cBy*math.cos(x_rot) - cBz*math.sin(x_rot)} == 0?")
        cBz = round(cBy*math.sin(x_rot) + cBz*math.cos(x_rot), 2)
        cCy_temp = round(cCy, 2)
        cCy = round(cCy_temp*math.cos(x_rot) - cCz*math.sin(x_rot), 2)
        cCz = round(cCy_temp*math.sin(x_rot) + cCz*math.cos(x_rot), 2)

        # Rotate B around Y axis till Z=0, -xsin(theta) + zcos(theta)=0, theta=atan(x/z)

        y_rot = round(math.atan(cBz/cBx) , 2)
        # print(f"y_rot == {y_rot}")
        # Cbz == 0?
        # print(f"{cBz*math.cos(y_rot) - cBx*math.sin(y_rot)} == 0?")
        cBx = round(cBx*math.cos(y_rot) + cBz*math.sin(y_rot), 2)
        cCx_temp = round(cCx, 2)
        cCx = round(cCx_temp*math.cos(y_rot) + cCz*math.sin(y_rot), 2)
        cCz = round(cCz*math.cos(y_rot) - cCx_temp*math.sin(y_rot), 2)

        #ysin(theta) + zcos(theta)=0

        theta = round(math.atan(-cCz/cCy), 2)
        cCy = round(cCy*math.cos(theta) - cCz*math.sin(theta) , 2)
        
        #calculate midway result
        x = round((dA**2 - dB**2 + cBx**2) / (2*cBx), 2)
        y = round((dA**2 - dC**2 + cCx**2 + cCy**2 - 2*cCx*x) / (2*cCy), 2)
   
    except:
        print("Math error in Alternative trilateration algo")
        return UnityCoordinate(-555, -555, -555)
   
    d = round(dA**2 - x**2 - y**2, 2)
   
    if (d < 0):
        print(f"Trilateration impossible: d({d}) < 0")
        return UnityCoordinate(d, -999, -999)
    
    print(f"Z == +-{math.sqrt(d)}, but we take the average (0)")
    z = round(0, 2)
    z_1 = round(math.sqrt(d), 2)
    z_2 = round(-math.sqrt(d), 2)
    
    #rotate back, x y x
    y_temp_1 = round(y, 2)
    y_1 = round(y_temp_1*math.cos(-theta), 2) # -z*sin
    z_1 = round(y_temp_1*math.sin(-theta), 2) # +z*cos
    x_temp_1 = round(x, 2)
    x_1 = round(x_temp_1*math.cos(-y_rot) + z_1*math.sin(-y_rot), 2)
    z_1 = round(z_1*math.cos(-y_rot) - x_temp_1*math.sin(-y_rot), 2)
    y_temp_1 = round(y_1, 2)
    y_1 = round(y_temp_1*math.cos(-x_rot) - z_1*math.sin(-x_rot), 2)
    z_1 = round(y_temp_1*math.sin(-theta) + z_1*math.cos(-x_rot), 2)
    print(f"with z1 == ({x_1}, {y_1}, {z_1})")

    y_temp_2 = round(y, 2)
    y_2 = round(y_temp_2*math.cos(-theta) -z_1*math.sin(-theta), 2)
    z_2 = round(y_temp_2*math.sin(-theta) +z_1*math.cos(-theta), 2)
    x_temp_2 = round(x, 2)
    x_2 = round(x_temp_2*math.cos(-y_rot) + z_2*math.sin(-y_rot), 2)
    z_2 = round(z_2*math.cos(-y_rot) - x_temp_2*math.sin(-y_rot), 2)
    y_temp_2 = round(y_2, 2)
    y_2 = round(y_temp_2*math.cos(-x_rot) - z_2*math.sin(-x_rot), 2)
    z_2 = round(y_temp_2*math.sin(-theta) + z_2*math.cos(-x_rot), 2)
    print(f"with z2 == ({x_2}, {y_2}, {z_2})")

    y_temp = round(y, 2)
    y = round(y_temp*math.cos(-theta) -z_2*math.sin(-theta), 2)
    z = round(y_temp*math.sin(-theta) +z_2*math.cos(-theta), 2)
    x_temp = round(x, 2)
    x = round(x_temp*math.cos(-y_rot) + z*math.sin(-y_rot), 2)
    z = round(z*math.cos(-y_rot) - x_temp*math.sin(-y_rot), 2)
    y_temp = round(y, 2)
    y = round(y_temp*math.cos(-x_rot) - z*math.sin(-x_rot), 2)
    z = round(y_temp*math.sin(-theta) + z*math.cos(-x_rot), 2)

    #translate back
    x += cAx
    y += cAy
    z += cAz

    return UnityCoordinate(x, y, z)

# https://arxiv.org/pdf/1912.07801
# input: coordinates x1, y1 to xn, yn; distances d1 to dn
# Construct a 2 by n matrix A as in column 1 the difference between x1 to xn-1 and xn multiplied by -2
# and in column 2 the difference between y1 and yn-1 and yn multiplied by -2
# Then construct matrix B as a column matrix of difference of the square of d1 to dn-1 and the square of dn
# minus the difference of the square of x1 to xn-1 and the square of xn
# minus the difference of the square of y1 to yn-1 and the square of yn
# Find the (left) inverse of A, catching if none exist
# The estimated coordinate is the product of the inverse of A times B
# This doesn't take height difference in APs into account.
# since the coords are encoded with y as the height, z takes the role of "y"
def Multilateration2D (coords: list, distances: list):
    if len(coords) < 3 or len(distances) < 3:
        print("Too few data points for multilateration")
        return UnityCoordinate(-777, -777, -777)

    last_coord = coords[-1]
    coords = coords[:-1]
    last_distance = distances[-1]
    distances = distances[:-1]
    
    matrix_form_A = []
    matrix_form_B = []
    for coord, distance in zip(coords, distances):
        matrix_form_A.append([
            -2 * (coord.x - last_coord.x), 
            -2 * (coord.z - last_coord.z)
        ])

        matrix_form_B.append([
            (distance ** 2 - last_distance ** 2) -
            (coord.x ** 2 - last_coord.x ** 2) -
            (coord.z ** 2 - last_coord.z ** 2)
            ])
        
    matrix_A = np.matrix(matrix_form_A)    
    matrix_B = np.matrix(matrix_form_B)

    # TODO: uncaught errors?
    inverse_A = np.linalg.pinv(matrix_A)

    result = np.matmul(inverse_A, matrix_B)
    # print(f"Multilateration result: ({result[0, 0]},{last_coord.y},{result[1, 0]})")
    
    # Since we assume the difference in height to be trivial, we take any y coordinate
    return UnityCoordinate(result[0, 0], last_coord.y, result[1, 0])

# https://www-sciencedirect-com.vu-nl.idm.oclc.org/science/article/pii/S0140366408004751?via%3Dihub
# Works on 4 points and 4 distances
def MobileTrilateration(coords: list, distances: list):
    G = np.array([
        [coords[1].x - coords[0].x, coords[1].y - coords[0].y, coords[1].z - coords[0].z],
        [coords[3].x - coords[0].x, coords[2].y - coords[0].y, coords[2].z - coords[0].z],
        [coords[2].x - coords[0].x, coords[3].y - coords[0].y, coords[3].z - coords[0].z],
        ])
    sq_coords = list(map(lambda p: UnityCoordinate(p.x**2, p.y**2, p.z**2), coords))
    sq_distances = list(map(lambda d: d**2, distances))
    h = np.array(
        [
            .5*(sq_coords[1].x + sq_coords[1].y + sq_coords[1].z - sq_coords[0].x - sq_coords[0].y - sq_distances[1] + sq_distances[0]),
            .5*(sq_coords[2].x + sq_coords[2].y + sq_coords[2].z - sq_coords[0].x - sq_coords[0].y - sq_distances[2] + sq_distances[0]),
            .5*(sq_coords[3].x + sq_coords[3].y + sq_coords[3].z - sq_coords[0].x - sq_coords[0].y - sq_distances[3] + sq_distances[0]),
        ])
    
    try:
        G_inverse = np.linalg.inv(G)
        p = G_inverse @ h 
    except Exception as e:
        print(e)
        return UnityCoordinate(-333, -333, -333)
    
    # print(p)
    return UnityCoordinate(p[0], p[1], p[2])
