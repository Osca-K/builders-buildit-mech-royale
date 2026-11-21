"""Geometric firing regressions independent of the recorded protocol stream."""
import math
import unittest
from bot import cylinder_aligned, target_size


class AimTests(unittest.TestCase):
    def test_hit_above_center(self):
        self.assertTrue(cylinder_aligned([0,0,7], [0,0], [30,0,4.5], 2.5,9))

    def test_miss_above_or_beside_target(self):
        self.assertFalse(cylinder_aligned([0,0,12], [0,0], [30,0,4.5],2.5,9))
        self.assertFalse(cylinder_aligned([0,0,7], [.2,0], [30,0,4.5],2.5,9))

    def test_target_behind(self):
        self.assertFalse(cylinder_aligned([0,0,7], [math.pi,0], [30,0,4.5],2.5,9))

    def test_cubes_scale_without_stat_cap(self):
        config={'mech':{'radius':2.5,'height':9},'cubes':{'size_per_cube':.05}}
        self.assertEqual(target_size({'kind':'mech','cubes':20},config),(5.,18.))


if __name__=='__main__':
    unittest.main()
