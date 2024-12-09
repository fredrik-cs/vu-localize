from src.coordinates import MeterToUnity, UnityCoordinate, UnityToMeter

def AnalyticalDistanceToAP(power, base_power = -47.0, environmental_factor = 4.0):
    ### power = measured signal right now
    ### base_power = signal strength at 1 meter. 
    #   -47 is measured from one AP, but different APs could have different base powers.
    #   could look into effect of specifying base power for known APs
    ### environmental factor = a factor between 2 and 4 that increases the less free the space is
    power = float(power)
    return 10.0 ** ((base_power - power)/(10.0 * environmental_factor))

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
    
    M = (A*F*K) - (A*G*J) - (B*E*K) + (B*G*I) + (C*E*J) - (C*F*I)
    M1 = (D*F*K) - (D*G*J) - (B*H*K) + (B*G*L) + (C*H*J) - (C*F*L)
    M2 = (A*H*K) - (A*G*L) - (D*E*K) + (D*G*I) + (C*E*L) - (C*H*I)
    M3 = (A*F*L) - (A*H*J) - (B*E*L) + (B*H*I) + (D*E*J) - (D*F*I)
    
    x = MeterToUnity(M1/M)
    y = MeterToUnity(M2/M)
    z = MeterToUnity(M3/M)
    
    return UnityCoordinate(x, y, z)