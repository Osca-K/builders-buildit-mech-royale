"""Geometric firing regressions independent of the recorded protocol stream."""
import math
import unittest
from bot import Bot


class AimTests(unittest.TestCase):
    def test_reaches_cube_from_old_stop_distance(self):
        config={'mech':{},'cubes':{},'loot':{'pickup_radius':4}}
        bot=Bot({'config':config,'seed':1,'slot':0,'map':{'dir':'/missing-arena'}})
        obs={'tick':0,'t':0,'zone':{'center':[0,0],'radius':200,
             'next_center':[0,0],'next_radius':150},
             'self':{'pos':[0,0,0],'stats':{},'hp':1400,'max_hp':1400,
                     'cubes':0,'in_zone':True,'energy':100,'grounded':True,
                     'weapons':[None,None],'aim':[0,0]},
             'mechs':[],'drops':[],'cubes':[{'id':1,'pos':[4.5,0,0]}],
             'pickups':[],'projectiles':[],'crates':[],'offer':None}
        action=bot.act(obs)
        self.assertGreater(action['move'][0],0)


if __name__=='__main__':
    unittest.main()
