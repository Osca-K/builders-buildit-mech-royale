import math
import unittest
from bot import Arena, Bot, ballistic_solutions


class MortarTests(unittest.TestCase):
    def impact(self,origin,solution,speed=72,gravity=22,offset=3):
        t,yaw,pitch=solution
        direction=(math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch))
        point=[origin[i]+direction[i]*(offset+speed*t) for i in range(3)]
        point[2]-=.5*gravity*t*t
        return point

    def test_stationary_low_and_high_arcs_hit_with_barrel_offset(self):
        origin=[0,0,9.5]; target=[170,0,4.5]
        arcs=ballistic_solutions(origin,target,[0,0,0],72,22,3)
        self.assertEqual(len(arcs),2)
        self.assertLess(arcs[0][2],arcs[1][2])
        for arc in arcs:
            self.assertLess(math.dist(self.impact(origin,arc),target),1e-6)

    def test_moving_target_intercept(self):
        origin=[0,0,9.5];target=[100,0,4.5];velocity=[0,11.7,0]
        arcs=ballistic_solutions(origin,target,velocity,72,22,3)
        self.assertTrue(arcs)
        for arc in arcs:
            predicted=[target[i]+velocity[i]*arc[0] for i in range(3)]
            self.assertLess(math.dist(self.impact(origin,arc),predicted),1e-6)

    def test_rooftop_target_height(self):
        origin=[0,0,9.5];target=[100,0,34.5]
        for arc in ballistic_solutions(origin,target,[0,0,0],72,22,3):
            self.assertLess(math.dist(self.impact(origin,arc),target),1e-6)

    def test_unreachable_target_has_no_arc(self):
        self.assertEqual(ballistic_solutions([0,0,9.5],[400,0,4.5],[0,0,0],72,22,3),[])

    def test_overhead_solid_blocks_low_but_not_high_arc(self):
        arena=Arena('/missing-arena')
        ring=[50,-10,60,-10,60,10,50,10]
        item=(10,35,ring,[],(50,-10,60,10))
        for x in (1,2):
            for y in (-1,0):
                arena.buckets[(x,y)]=[item]
        origin=[0,0,9.5]
        arcs=ballistic_solutions(origin,[170,0,4.5],[0,0,0],72,22,3)
        self.assertTrue(arena.los([0,0,7],[170,0,4.5]))
        self.assertFalse(arena.arc_clear(origin,arcs[0],72,22,3))
        self.assertTrue(arena.arc_clear(origin,arcs[1],72,22,3))

    def observation(self,distance=70,cooldown=0):
        config={'mech':{},'cubes':{},'loot':{'pickup_radius':4},'weapons':{'mortar':{'gravity':22}}}
        bot=Bot({'config':config,'seed':1,'slot':0,'map':{'dir':'/missing-arena'}})
        arc=ballistic_solutions([0,0,9.5],[distance,0,4.5],[0,0,0],72,22,3)[0]
        return bot,{'tick':0,'t':0,'zone':{'center':[0,0],'radius':200,'next_center':[0,0],'next_radius':150},
             'self':{'pos':[0,0,0],'vel':[0,0,0],'stats':{},'hp':1400,'max_hp':1400,
                     'cubes':0,'in_zone':True,'energy':100,'grounded':True,'aim':[arc[1],arc[2]],
                     'weapons':[{'kind':'gun','ammo':12,'stats':{'speed':252,'range':230}},
                                {'kind':'mortar','cooldown':cooldown,'stats':{'speed':72,'gravity':22}}]},
             'mechs':[{'id':1,'kind':'mech','pos':[distance,0,0],'vel':[0,0,0],'hp':1400}],
             'drops':[],'cubes':[],'pickups':[],'projectiles':[],'crates':[],'offer':None}

    def test_ready_mortar_fires_only_when_torso_matches_arc(self):
        bot,obs=self.observation()
        action=bot.act(obs)
        self.assertEqual(action['fire'],[False,True])
        obs['self']['aim']=[0,-.04]
        self.assertFalse(bot.act(obs)['fire'][1])

    def test_close_target_cannot_trigger_self_splash(self):
        bot,obs=self.observation(distance=15)
        self.assertFalse(bot.act(obs)['fire'][1])

    def test_cooldown_immediately_resumes_gun_aim(self):
        bot,obs=self.observation(cooldown=2.5)
        obs['self']['aim']=[0,math.atan2(-2.5,70)]
        action=bot.act(obs)
        self.assertEqual(action['fire'],[True,False])

    def test_one_bullet_kill_does_not_delay_for_mortar(self):
        bot,obs=self.observation()
        obs['mechs'][0]['hp']=30
        obs['self']['aim']=[0,math.atan2(-2.5,70)]
        self.assertEqual(bot.act(obs)['fire'],[True,False])


if __name__=='__main__':
    unittest.main()
