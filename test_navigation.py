from pathlib import Path
import time
import unittest
from bot import Arena


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arena=Arena(Path(__file__).with_name('arena'))

    def test_real_underpass_fits_starter_but_not_ten_cube_mech(self):
        arena=self.arena
        start=[-119,-63,arena.height(-119,-63)]
        goal=[-119,-7]
        original=arena.route(start,goal)
        self.assertIn((-119,-35),original)
        self.assertIn((-119,-28),original)
        grown=arena.route(start,goal,4.25,13.5)
        self.assertTrue(grown)
        self.assertNotIn((-119,-35),grown)
        self.assertNotIn((-119,-28),grown)
        self.assertTrue(all(not arena.solid(x,y,arena.height(x,y),4.25,13.5) for x,y in grown))

    def test_body_checks_are_cached(self):
        arena=self.arena
        cache={}
        calls=[]
        original=arena.solid
        arena.solid=lambda *args:(calls.append(args) or original(*args))
        try:
            self.assertTrue(arena.body_blocked((-17,-5),4.25,13.5,cache))
            self.assertTrue(arena.body_blocked((-17,-5),4.25,13.5,cache))
            self.assertEqual(len(calls),1)
        finally:
            arena.solid=original

    def test_search_timeout_returns_a_safe_partial_path(self):
        arena=self.arena
        previous=arena.route_budget
        arena.route_budget=0.
        try:
            before=time.perf_counter()
            path=arena.route([-119,-63,arena.height(-119,-63)],[-119,-7],4.25,13.5)
            self.assertLess(time.perf_counter()-before,.05)
            self.assertEqual(path,[])
        finally:
            arena.route_budget=previous

    def test_only_four_body_dimension_caches_are_retained(self):
        arena=self.arena
        for count in range(15):
            arena.route([0,0,0],[0,0],4.+count*.1,14.+count*.1)
        self.assertLessEqual(len(arena.body_masks),4)


if __name__=='__main__':
    unittest.main()
