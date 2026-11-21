import math
import unittest
from bot import Bot, target_point


class TargetingTests(unittest.TestCase):
    config={'mech':{'min_pitch':-.7,'max_pitch':1.3},'cubes':{},'loot':{'pickup_radius':4}}

    def target(self,x,z=0,cubes=0):
        return {'id':1,'kind':'mech','pos':[x,0,z],'vel':[0,0,0],
                'hp':1400,'cubes':cubes}

    def test_ground_level_point_is_unchanged(self):
        self.assertEqual(target_point([0,0,7],self.target(50),self.config,{}),[50,0,4.5])

    def test_entire_body_below_minimum_pitch_is_rejected(self):
        self.assertIsNone(target_point([0,0,37],self.target(10),self.config,{}))

    def test_reachable_upper_body_is_retained(self):
        point=target_point([0,0,15],self.target(10,cubes=10),self.config,{})
        self.assertIsNotNone(point)
        self.assertGreaterEqual(math.atan2(point[2]-15,10),-.7-1e-12)
        self.assertLess(point[2],13.5)

    def test_lightning_yaw_only_arc_is_retained(self):
        lightning={'stats':{'range':45}}
        self.assertEqual(target_point([0,0,37],self.target(10),self.config,{},lightning),[10,0,4.5])

    def test_unreachable_nearest_target_does_not_hide_valid_gun_shot(self):
        bot=Bot({'config':self.config,'seed':1,'slot':0,'map':{'dir':'/missing-arena'}})
        pitch=math.atan2(4.5-37,70)
        obs={'tick':0,'t':0,'zone':{'center':[0,0],'radius':200,'next_center':[0,0],'next_radius':150},
             'self':{'pos':[0,0,30],'vel':[0,0,0],'stats':{},'hp':1400,'max_hp':1400,
                     'cubes':0,'in_zone':True,'energy':100,'grounded':True,'aim':[0,pitch],
                     'weapons':[{'kind':'gun','ammo':12,'stats':{'speed':252,'range':230}},None]},
             'mechs':[self.target(10),dict(self.target(70),id=2)],'drops':[],'cubes':[],
             'pickups':[],'projectiles':[],'crates':[],'offer':None}
        action=bot.act(obs)
        self.assertEqual(bot.focus,2)
        self.assertTrue(action['fire'][0])


if __name__=='__main__':
    unittest.main()
