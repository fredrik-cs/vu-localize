import unittest
from coordinates import UnityCoordinate
from trilateration import Trilaterate2D, Trilaterate3D, Trilaterate3DAlternate, Multilateration2D, MobileTrilateration

THREE_SUCCESS = [
    UnityCoordinate(1,2,2),
    UnityCoordinate(2,3,6),
    UnityCoordinate(1,4,8),
    3,7,9]
THREE_SUCCESS_RESULT = UnityCoordinate(0, 0, 0)
FOUR_SUCCESS = [
    [
    UnityCoordinate(1,2,2),
    UnityCoordinate(2,3,6),
    UnityCoordinate(4,4,7),
    UnityCoordinate(8,9,12),
    ],
    [3,7,9,17]]
FOUR_SUCCESS_RESULT = UnityCoordinate(0, 0, 0)

class TestMultilateration(unittest.TestCase):

    def test_tl_alt(self):

        self.assertEqual(Trilaterate3DAlternate(*THREE_SUCCESS), THREE_SUCCESS_RESULT, "Should be 0")

if __name__ == "__main__":
    unittest.main()