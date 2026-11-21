"""Reactive movement/loot micro-scenario, not a full match simulator.

The scene implements the documented 20Hz acceleration, energy and gravity
rules and removes a cube only when the actual moving body reaches its pickup
volume. It does not model opponents, damage, terrain or full server physics.
"""
import math
import unittest
from bot import Bot


def harvest_scene(bot_class=Bot,duration=12.,wall=False):
    config={'mech':{'walk_speed':11.7,'boost_speed':19.5,'ground_accel':58.5,
                   'air_accel':12.,'gravity':22.,'jump_speed':11.,'jet_accel':34.,
                   'max_rise_speed':10.,'energy_regen':18.,'energy_regen_delay':.6,
                   'boost_drain':17.,'jet_drain':15.},
            'cubes':{'pickup_radius':3.5},'loot':{'pickup_radius':4.},
            'weapons':{'mortar':{'gravity':22.}}}
    bot=bot_class({'config':config,'seed':1,'slot':0,'map':{'dir':'/missing-arena'}})
    p=[0.,0.,0.];v=[0.,0.,0.];energy=100.;grounded=True;cube=True
    last_spent=-100.;jumps=jets=0;pickup_at=None
    goal=[30.,0.] if wall else [4.5,0.]
    for i in range(round(duration/.1)):
        t=i*.1
        obs={'tick':i*2,'t':t,'zone':{'center':goal,'radius':200.,'next_center':goal,'next_radius':150.},
             'self':{'pos':p[:],'vel':v[:],'stats':config['mech'],'hp':1400.,'max_hp':1400.,
                     'cubes':0 if cube else 1,'in_zone':True,'energy':energy,'max_energy':100.,
                     'grounded':grounded,'weapons':[None,None],'aim':[0.,0.]},
             'mechs':[],'drops':[],'cubes':[{'id':5000,'pos':[4.5,0.,0.]}] if cube and not wall else [],
             'pickups':[],'projectiles':[],'crates':[],'offer':None}
        action=bot.act(obs)
        if action.get('jump') and grounded:
            v[2]=11.;grounded=False;jumps+=1
        for step in range(2):
            clock=t+step*.05
            boost=action.get('boost',False) and energy>0
            speed=19.5 if boost and grounded else 11.7
            direction=action.get('move',[0.,0.])
            length=max(1.,math.hypot(*direction))
            desired=[direction[j]/length*speed for j in range(2)]
            delta=[desired[j]-v[j] for j in range(2)]
            acceleration=58.5 if grounded else 12.
            fraction=min(1.,acceleration*.05/math.hypot(*delta)) if math.hypot(*delta) else 0.
            for j in range(2):
                v[j]+=delta[j]*fraction
                p[j]+=v[j]*.05
            if wall:
                p[0]=0.;v[0]=0.
            spending=0.
            if boost and not grounded:
                v[2]=min(10.,v[2]+34.*.05);spending=15.;jets+=1
            elif boost and math.hypot(*direction)>0:
                spending=17.
            if not grounded:
                v[2]-=22.*.05;p[2]+=v[2]*.05
                if p[2]<=0:
                    p[2]=v[2]=0.;grounded=True
            if spending:
                energy=max(0.,energy-spending*.05);last_spent=clock
            elif clock-last_spent>=.6:
                energy=min(100.,energy+18.*.05)
            if cube and not wall and math.hypot(p[0]-4.5,p[1])<=3.5 and abs(p[2])<=4.:
                cube=False;pickup_at=clock
    return {'picked':not cube,'pickup_at':pickup_at,'energy':energy,
            'jumps':jumps,'jet_ticks':jets,'position':p}


class HarvestTests(unittest.TestCase):
    def test_pickup_then_preserve_energy_at_intentional_arrival(self):
        result=harvest_scene()
        self.assertTrue(result['picked'])
        self.assertLess(result['pickup_at'],1.)
        self.assertEqual(result['energy'],100.)
        self.assertEqual(result['jumps'],0)
        self.assertEqual(result['jet_ticks'],0)

    def test_real_blockage_still_activates_jump_and_jet(self):
        result=harvest_scene(duration=3.,wall=True)
        self.assertGreater(result['jumps'],0)
        self.assertGreater(result['jet_ticks'],0)
        self.assertLess(result['energy'],100.)


if __name__=='__main__':
    unittest.main()
