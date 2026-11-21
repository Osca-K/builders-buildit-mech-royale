"""Placement-first mech controller. All physics constants come from hello/stats."""
import heapq
import json
import math
from pathlib import Path
import random
import mechfight as mf


def norm(dx, dy):
    d = math.hypot(dx, dy)
    return (dx / d, dy / d) if d > 1e-8 else (0., 0.)


def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])


def angle(a, b):
    return (a-b+math.pi) % (2*math.pi)-math.pi


def inside(x, y, ring):
    hit = False
    j = len(ring)-2
    for i in range(0, len(ring), 2):
        ax, ay, bx, by = ring[i], ring[i+1], ring[j], ring[j+1]
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:
            hit = not hit
        j = i
    return hit


class Arena:
    def __init__(self, folder):
        self.prisms = []
        self.buckets = {}
        self.blocked = set()
        self.cell = 7.
        try:
            world = json.loads((Path(folder)/'v2/world.json').read_text())
            for p in world['prisms']:
                r = p['ring']
                box = (min(r[::2]),min(r[1::2]),max(r[::2]),max(r[1::2]))
                item = (p['base'],p['top'],r,p.get('holes',[]),box)
                self.prisms.append(item)
                for ix in range(math.floor((box[0]-5)/28),math.floor((box[2]+5)/28)+1):
                    for iy in range(math.floor((box[1]-5)/28),math.floor((box[3]+5)/28)+1):
                        self.buckets.setdefault((ix,iy),[]).append(item)
            # Ground navigation mask; local steering handles elevation/bridges.
            terrain = world['terrain']
            import array
            heights = array.array('h')
            heights.frombytes((Path(folder)/'v2/terrain.i16').read_bytes())
            self.terrain, self.heights = terrain, heights
            for item in self.prisms:
                box = item[-1]
                for ix in range(math.floor((box[0]-4)/self.cell), math.ceil((box[2]+4)/self.cell)+1):
                    for iy in range(math.floor((box[1]-4)/self.cell), math.ceil((box[3]+4)/self.cell)+1):
                        x,y=ix*self.cell,iy*self.cell
                        if self.solid(x,y,self.height(x,y),3.2,9.):
                            self.blocked.add((ix,iy))
        except (OSError,ValueError,KeyError):
            pass

    def height(self,x,y):
        if not hasattr(self,'terrain'):
            return 0.
        t=self.terrain
        i=max(0,min(t['nx']-1,int((x-t['minX'])/t['step'])))
        j=max(0,min(t['ny']-1,int((y-t['minY'])/t['step'])))
        return self.heights[j*t['nx']+i]/100.

    def solid(self,x,y,z,r=2.8,h=9.):
        for base,top,ring,holes,box in self.buckets.get((math.floor(x/28),math.floor(y/28)),[]):
            if top<=z+1.15 or base>=z+h+.2:
                continue
            if x+r<box[0] or x-r>box[2] or y+r<box[1] or y-r>box[3]:
                continue
            for dx,dy in ((0,0),(r,0),(-r,0),(0,r),(0,-r),(r*.7,r*.7),(-r*.7,r*.7),(r*.7,-r*.7),(-r*.7,-r*.7)):
                if inside(x+dx,y+dy,ring) and not any(inside(x+dx,y+dy,hole) for hole in holes):
                    return True
        return False

    def los(self,a,b):
        steps=max(1,int(math.dist(a,b)/3))
        for i in range(1,steps):
            f=i/steps
            x,y,z=[a[j]+(b[j]-a[j])*f for j in range(3)]
            for base,top,ring,holes,box in self.buckets.get((math.floor(x/28),math.floor(y/28)),[]):
                if base<z<top and box[0]<=x<=box[2] and box[1]<=y<=box[3] and inside(x,y,ring) and not any(inside(x,y,hole) for hole in holes):
                    return False
            if z<self.height(x,y):
                return False
        return True

    def route(self,p,goal):
        c=self.cell
        start=(round(p[0]/c),round(p[1]/c))
        end=(round(goal[0]/c),round(goal[1]/c))
        if end in self.blocked:
            options=[(end[0]+dx,end[1]+dy) for dx in range(-5,6) for dy in range(-5,6)]
            end=min((a for a in options if a not in self.blocked),key=lambda a:distance(a,end),default=start)
        queue=[(distance(start,end),0.,start)]
        costs={start:0.}
        parents={}
        best=start
        for _ in range(3000):
            if not queue:
                break
            _,cost,node=heapq.heappop(queue)
            if cost!=costs[node]:
                continue
            if distance(node,end)<distance(best,end):
                best=node
            if node==end:
                best=node
                break
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                nxt=(node[0]+dx,node[1]+dy)
                if nxt in self.blocked or (dx and dy and ((node[0]+dx,node[1]) in self.blocked or (node[0],node[1]+dy) in self.blocked)):
                    continue
                nc=cost+(1.41421356 if dx and dy else 1.)
                if nc<costs.get(nxt,1e30):
                    costs[nxt]=nc
                    parents[nxt]=node
                    heapq.heappush(queue,(nc+distance(nxt,end),nc,nxt))
        path=[]
        while best!=start and best in parents:
            path.append((best[0]*c,best[1]*c))
            best=parents[best]
        return path[::-1]


class Bot:
    name='Aegis-14'

    def __init__(self,hello):
        self.config=hello['config']
        self.arena=Arena(hello['map']['dir'])
        self.rng=random.Random(hello['seed'])
        self.side=1 if hello['slot']%2 else -1
        self.path=[]
        self.path_goal=None
        self.last_route=-100
        self.prev=None
        self.stuck=0.
        self.lightning_rest=False
        self.focus=None

    def act(self,o):
        me=o['self']; p=me['pos']; t=o['t']; zone=o['zone']
        stats=me['stats']; hp=me['hp']/max(1,me['max_hp'])
        radius=stats.get('radius',2.5*(1+.05*me['cubes']))
        height=stats.get('height',9*(1+.05*me['cubes']))
        center=zone['next_center']; zr=zone['next_radius']
        # Move toward the next circle early, retaining space to kite at its edge.
        safe=max(0,zr-max(8,radius*2))
        urgent=not me['in_zone'] or distance(p,zone['center'])>zone['radius']-18
        enemies=[e for e in o['mechs'] if e['kind']=='mech']
        nearest=min(enemies,key=lambda e:distance(p,e['pos']),default=None)
        nd=distance(p,nearest['pos']) if nearest else 1e9
        lightning=next((w for w in me['weapons'] if w and w['kind']=='lightning'),None)
        if me['energy']<12:self.lightning_rest=True
        elif me['energy']>65:self.lightning_rest=False
        recovering=hp<.68 and nd>75
        goal=list(center)
        # Health restoration from uncontested drops can outweigh combat loot.
        drops=[d for d in o['drops'] if d['lands_in']<8 and distance(d['pos'],center)<max(0,zr-10)
               and not any(distance(e['pos'],d['pos'])<40 for e in enemies)]
        if drops and hp<.85 and not urgent:
            goal=min(drops,key=lambda d:distance(p,d['pos']))['pos'][:2]
        elif not urgent:
            loot=[]
            for c in o['cubes']:
                if abs(c['pos'][2]-p[2])<6:
                    loot.append((distance(p,c['pos'])-35,c['pos']))
            kinds=[w['kind'] for w in me['weapons'] if w]
            for q in o['pickups']:
                if q['kind'] not in kinds and abs(q['pos'][2]-p[2])<5:
                    value={'lightning':85,'laser':25,'mortar':-100,'gun':-100}[q['kind']]
                    if len(kinds)<2 or q['kind']=='lightning':
                        loot.append((distance(p,q['pos'])-value,q['pos']))
            loot=[(s,q) for s,q in loot if distance(q,center)<safe and not any(distance(e['pos'],q)<35 for e in enemies)]
            if loot and min(loot,key=lambda v:v[0])[0]<55:
                goal=min(loot,key=lambda v:v[0])[1][:2]
            elif nearest and nd<100:
                ex,ey=norm(p[0]-nearest['pos'][0],p[1]-nearest['pos'][1])
                desired=(lightning['stats'].get('range',45)*.78 if lightning and not self.lightning_rest and hp>.36 else 75)
                goal=[nearest['pos'][0]+ex*desired-ey*16*self.side,
                      nearest['pos'][1]+ey*desired+ex*16*self.side]
            elif not nearest or nd>115:
                crates=[c for c in o['crates'] if distance(p,c['pos'])<75 and abs(c['pos'][2]-p[2])<5 and distance(c['pos'],center)<safe]
                if crates:goal=min(crates,key=lambda c:distance(p,c['pos']))['pos'][:2]
        d=distance(goal,center)
        if d>safe and d>0:
            goal=[center[0]+(goal[0]-center[0])*safe/d,center[1]+(goal[1]-center[1])*safe/d]
        if t-self.last_route>2 or self.path_goal is None or distance(goal,self.path_goal)>20:
            self.path=self.arena.route(p,goal)
            self.path_goal=goal
            self.last_route=t
        while self.path and distance(p,self.path[0])<7:
            self.path.pop(0)
        waypoint=self.path[0] if self.path else goal
        base=math.atan2(waypoint[1]-p[1],waypoint[0]-p[0])
        if self.prev and distance(p,self.prev)<.15:
            self.stuck+=.1
        else:
            self.stuck=0.
        self.prev=p[:]
        speed=stats.get('walk_speed',11.7)
        best=(-1e30,0.,0.)
        for off in (0,.3,-.3,.65,-.65,1.,-1.,1.5,-1.5,2.,-2.,math.pi):
            a=base+off; vx,vy=math.cos(a),math.sin(a)
            q=[p[0]+vx*7,p[1]+vy*7,p[2]]
            if self.arena.solid(q[0],q[1],p[2],radius+.5,height):
                continue
            if self.arena.height(q[0],q[1])-p[2]>5:
                continue
            score=(distance(p,waypoint)-distance(q,waypoint))*3-abs(off)*.5
            score-=max(0,distance(q,zone['center'])-zone['radius']+8)*12
            for e in enemies:
                ed=distance(q,e['pos'])
                score-=max(0,(90 if hp<.65 else 40)-ed)*(.55 if hp<.65 else .3)
            for bullet in o['projectiles']:
                bp,bv=bullet['pos'],bullet['vel']
                rx,ry=bp[0]-p[0],bp[1]-p[1]
                ux,uy=bv[0]-vx*speed,bv[1]-vy*speed
                den=ux*ux+uy*uy
                tau=max(0,min(.6,-(rx*ux+ry*uy)/den)) if den else 0
                miss=math.hypot(rx+ux*tau,ry+uy*tau)
                if abs(bp[2]+bv[2]*tau-(p[2]+height*.5))<height*.7:
                    score-=max(0,radius+4-miss)*7
            if score>best[0]:
                best=(score,vx,vy)
        disengaging=hp<.45 and nd<100 and me['energy']>40 and me['grounded'] and not self.lightning_rest
        closing=bool(lightning and not self.lightning_rest and hp>.55 and nd>lightning['stats'].get('range',45)+8 and nd<100 and me['energy']>60)
        act={'tick':o['tick'],'move':[best[1],best[2]],'boost':bool((urgent and me['energy']>15) or disengaging or closing),
             'jump':bool(self.stuck>.7 and me['grounded'] and me['energy']>35),
             'fire':[False,False]}
        if self.stuck>.8 and not me['grounded'] and me['energy']>15:
            act['boost']=True
        if distance(p,goal)<5 and not nearest:
            act['move']=[0.,0.]
        # Magazine capacity and shorter reload improve sustained gun damage
        # more than the same tier's fire-rate increase. Lightning range/cone
        # and efficiency support our existing close-range fighting policy.
        priority={'nanites':130,'armor':145,'plating':160,'servos':150,
                  'gun_damage':140,'gun_rate':125,'gun_mag':155,'gun_velocity':135,
                  'laser_damage':125,'laser_charge':120,'lightning_efficiency':175,
                  'lightning_range':180,'lightning_chain':135,
                  'reactor':170 if lightning else 110,'jets':100,'capacitor':120,'gyros':100}
        if o['offer']:
            act['pick']=max(range(len(o['offer']['choices'])),key=lambda i:priority.get(o['offer']['choices'][i]['id'],45))
        kinds=[w['kind'] for w in me['weapons'] if w]
        for q in o['pickups']:
            if q['kind'] in kinds or q['kind']=='mortar':
                continue
            if distance(p,q['pos'])<self.config['loot']['pickup_radius'] and abs(p[2]-q['pos'][2])<4:
                if len(kinds)<2:
                    act['take']=q['id']; break
                if q['kind']=='lightning' and 'laser' in kinds and not any(w and w['kind']=='laser' and w.get('charge',0)>0 for w in me['weapons']):
                    act.update(take=q['id'],drop=next(i for i,w in enumerate(me['weapons']) if w and w['kind']=='laser')); break
        origin=[p[0],p[1],p[2]+stats.get('muzzle_height',7.)]
        targets=[]
        if not recovering:
            for e in o['mechs']:
                ep=e['pos'][:]; ep[2]+=4.5 if e['kind']=='mech' else 1.75
                dd=distance(p,ep)
                if dd<230 and self.arena.los(origin,ep):
                    score=dd+(30 if e['kind']=='npc' else 0)+e.get('hp',1000)*.025-(15 if e['id']==self.focus else 0)
                    targets.append((score,e,ep))
            if nd>80:
                for c in o['crates']:
                    cp=c['pos'][:];cp[2]+=2
                    if distance(p,cp)<110 and self.arena.los(origin,cp):
                        targets.append((distance(p,cp)-10,dict(c,vel=[0,0,0]),cp))
        if targets:
            _,target,ep=min(targets,key=lambda x:x[0]); vel=target.get('vel',[0,0,0])
            self.focus=target['id']
            laser=next((w for w in me['weapons'] if w and w['kind']=='laser'),None)
            direct=bool(laser and laser.get('charge',0)>=laser['stats'].get('charge',.75)-.05)
            gun=next((w for w in me['weapons'] if w and w['kind']=='gun'),None)
            aimpoint=ep[:]
            if gun and not direct:
                s=gun['stats'].get('speed',252.)
                rx=[ep[i]-origin[i] for i in range(3)]
                aa=sum(v*v for v in vel)-s*s; bb=2*sum(rx[i]*vel[i] for i in range(3)); cc=sum(v*v for v in rx)
                disc=bb*bb-4*aa*cc
                roots=[u for u in ((-bb-math.sqrt(disc))/(2*aa),(-bb+math.sqrt(disc))/(2*aa)) if u>0] if disc>=0 and abs(aa)>1e-8 else []
                flight=min(roots) if roots else math.sqrt(cc)/s
                aimpoint=[ep[i]+vel[i]*min(1.5,flight) for i in range(3)]
                if target.get('kind')=='mech' and abs(vel[2])>.2:
                    aimpoint[2]=max(self.arena.height(aimpoint[0],aimpoint[1])+4.5,
                                    aimpoint[2]-.5*self.config['mech'].get('gravity',22)*min(1.5,flight)**2)
            dx,dy,dz=[aimpoint[i]-origin[i] for i in range(3)]
            yaw,pitch=math.atan2(dy,dx),math.atan2(dz,math.hypot(dx,dy))
            act['aim']=[yaw,pitch]
            tolerance=max(.012,math.atan2(2.8,distance(p,ep)))
            aligned=abs(angle(yaw,me['aim'][0]))<tolerance and abs(pitch-me['aim'][1])<tolerance+.01
            for i,w in enumerate(me['weapons']):
                if not w: continue
                kind=w['kind']; ws=w['stats']; dd=distance(p,ep)
                if kind=='gun':
                    act['fire'][i]=bool(aligned and dd<ws.get('range',230))
                    if w.get('ammo',1)==0: act['reload']=True
                elif kind=='laser':
                    charge=w.get('charge',0)
                    act['fire'][i]=bool(w.get('cooldown',0)<=0 and dd<ws.get('range',280) and (charge<ws.get('charge',.75)-.03 or not aligned))
                elif kind=='lightning':
                    # Lightning selects its own nearest target in the actual
                    # torso cone. Gun lead/focus must not suppress a valid arc
                    # against a different nearby opponent while we turn.
                    arc_range=ws.get('range',45)-1
                    arc_cone=math.radians(ws.get('cone_deg',30))*.9
                    arc_target=any(math.dist(origin,tp)<arc_range and
                        abs(angle(math.atan2(tp[1]-origin[1],tp[0]-origin[0]),me['aim'][0]))<arc_cone
                        for _,_,tp in targets)
                    act['fire'][i]=bool(not self.lightning_rest and arc_target and me['energy']>8)
        else:
            if gun:=next((w for w in me['weapons'] if w and w['kind']=='gun'),None):
                if gun.get('ammo',12)<8: act['reload']=True
            act['aim']=[math.atan2(nearest['pos'][1]-p[1],nearest['pos'][0]-p[0]) if nearest else base+math.sin(t*.7)*1.3,0.]
        return act


if __name__=='__main__':
    mf.run(Bot)
