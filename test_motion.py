"""Physics boundary cases independent of the recorded conformance stream."""
import unittest
from bot import motion_path, projectile_clearance


class MotionTests(unittest.TestCase):
    def test_reversing_cannot_reverse_velocity_in_one_tick(self):
        path=motion_path([11.7,0,0],[-1,0],11.7,58.5,True,22)
        # Two 50ms server steps leave positive momentum after 100ms.
        self.assertAlmostEqual(path[2][0],.73125)
        self.assertGreater(path[2][0],0)

    def test_air_cannot_dodge_as_quickly_as_ground(self):
        ground=motion_path([0,0,0],[1,0],11.7,58.5,True,22)
        air=motion_path([0,0,0],[1,0],11.7,12,False,22)
        self.assertGreater(ground[2][0],air[2][0]*4)

    def test_fast_bullet_crossing_between_ticks_is_detected(self):
        path=[(0,0,0)]*13
        bullet={'kind':'gun','pos':[-6.3,1,4.5],'vel':[252,0,0]}
        self.assertAlmostEqual(projectile_clearance([0,0,0],path,9,bullet,22),1.)

    def test_vertical_overlap_is_clipped_before_minimizing(self):
        path=[(0,0,0)]*13
        # Horizontal closest approach is above the body; the shot intersects
        # the head later in the same interval and must still be considered.
        bullet={'kind':'gun','pos':[0,0,12],'vel':[20,0,-100]}
        self.assertAlmostEqual(projectile_clearance([0,0,0],path,9,bullet,22),.5)

    def test_mortar_fall_enters_body_from_above(self):
        path=[(0,0,0)]*13
        shell={'kind':'mortar','pos':[1,0,12],'vel':[0,0,0]}
        self.assertAlmostEqual(projectile_clearance([0,0,0],path,9,shell,22),1.)
        shell['kind']='gun'
        self.assertGreater(projectile_clearance([0,0,0],path,9,shell,22),1000)

    def test_reachable_reversal_does_not_invent_clearance(self):
        path=motion_path([11.7,0,0],[-1,0],11.7,58.5,True,22)
        bullet={'kind':'gun','pos':[2,9.5,4.5],'vel':[0,-90,0]}
        actual=projectile_clearance([0,0,0],path,9,bullet,22)
        instant=[(-11.7*i*.05,0,0) for i in range(13)]
        impossible=projectile_clearance([0,0,0],instant,9,bullet,22)
        self.assertLess(actual,2.5)
        self.assertGreater(impossible,2.5)


if __name__=='__main__':
    unittest.main()
