"""Deliberate resting must not activate the obstacle-escape jump/jet loop."""
import unittest
from bot import Bot


class StuckTests(unittest.TestCase):
    def observations(self,goal,airborne=False):
        config={'mech':{},'cubes':{'pickup_radius':3.5},'loot':{'pickup_radius':4}}
        bot=Bot({'config':config,'seed':1,'slot':0,'map':{'dir':'/missing-arena'}})
        actions=[]
        for i in range(15):
            obs={'tick':i*2,'t':i*.1,'zone':{'center':goal,'radius':200,
                 'next_center':goal,'next_radius':150},
                 'self':{'pos':[0,0,1 if airborne else 0],'stats':{},'hp':1400,'max_hp':1400,
                         'cubes':0,'in_zone':True,'energy':100,'grounded':not airborne,
                         'weapons':[None,None],'aim':[0,0]},
                 'mechs':[],'drops':[],'cubes':[],'pickups':[],
                 'projectiles':[],'crates':[],'offer':None}
            actions.append(bot.act(obs))
        return actions

    def test_deliberate_ground_rest_never_jumps(self):
        actions=self.observations([0,0])
        self.assertTrue(all(a['move']==[0,0] for a in actions))
        self.assertFalse(any(a['jump'] for a in actions))
        self.assertFalse(any(a['boost'] for a in actions))

    def test_deliberate_air_rest_never_jets(self):
        actions=self.observations([0,0],airborne=True)
        self.assertFalse(any(a['boost'] for a in actions))

    def test_blocked_ground_travel_still_jumps(self):
        actions=self.observations([30,0])
        self.assertTrue(any(a['jump'] for a in actions[8:]))

    def test_blocked_air_travel_still_jets(self):
        actions=self.observations([30,0],airborne=True)
        self.assertTrue(any(a['boost'] for a in actions[9:]))


if __name__=='__main__':
    unittest.main()
