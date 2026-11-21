import unittest
from bot import Bot


class ArrivalTests(unittest.TestCase):
    def action(self, cube):
        config={'mech':{},'cubes':{'pickup_radius':3.5},'loot':{'pickup_radius':4}}
        bot=Bot({'config':config,'seed':1,'slot':0,'map':{'dir':'/missing-arena'}})
        obs={'tick':0,'t':0,'zone':{'center':[4.5,0],'radius':200,
             'next_center':[4.5,0],'next_radius':150},
             'self':{'pos':[0,0,0],'stats':{},'hp':1400,'max_hp':1400,
                     'cubes':0,'in_zone':True,'energy':100,'grounded':True,
                     'weapons':[None,None],'aim':[0,0]},
             'mechs':[],'drops':[],'cubes':([{'id':1,'pos':[4.5,0,0]}] if cube else []),
             'pickups':[],'projectiles':[],'crates':[],'offer':None}
        return bot.act(obs)

    def test_collect_cube_inside_original_stop_radius(self):
        self.assertGreater(self.action(True)['move'][0],0)

    def test_preserve_circle_positioning_stop(self):
        self.assertEqual(self.action(False)['move'],[0.,0.])


if __name__=='__main__':
    unittest.main()
