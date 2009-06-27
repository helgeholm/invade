import random

import pyglet
from pyglet.window import key

class _Shield(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.sprites = [
            None,
            pyglet.resource.image('shield_damlo.png'),
            pyglet.resource.image('shield_damhi.png'),
            pyglet.resource.image('shield_full.png'),
            pyglet.resource.image('shield_nw.png'),
            pyglet.resource.image('shield_ne.png'),
            ]
        self.states = [
            [0, 4, 3, 3, 3, 3, 5, 0],
            [4, 3, 3, 3, 3, 3, 3, 5],
            [3, 3, 0, 0, 0, 0, 3, 3],
            [3, 3, 0, 0, 0, 0, 3, 3],
            ]
        self.IW = self.sprites[3].width
        self.IH = self.sprites[3].height
        self.RC = range(len(self.states))
        self.CC = range(len(self.states[0]))
        self.width = len(self.states[0]) * self.IW
    def update(self):
        pass
    def paint(self):
        for s_r in self.RC:
            for s_c in self.CC:
                s = self.sprites[self.states[s_r][s_c]]
                x = self.x + s_c * self.IW
                y = self.y - s_r * self.IH
                if s: s.blit(x, y)
    def absorb(self, xl, yl, xh, yh, fromAbove):
        x = (xl + xh) / 2
        for r in self.RC:
            ry = self.y - r * self.IH
            if yl >= ry + self.IH: continue
            if yh < ry: continue
            for c in self.CC:
                cx = self.x + c * self.IW
                if not self.states[r][c]: continue
                if x < cx: continue
                if x >= cx + self.IW: continue
                s = self.states[r][c]
                if s in [1, 2]:
                    n_s = 0
                elif s in [3, 4, 5]:
                    n_s = {True:1,False:2}[fromAbove]
                else:
                    assert False
                self.states[r][c] = n_s
                return True
        
class Shields(object):
    def __init__(self, window):
        sw = _Shield(0, 0).width
        pad = 128
        num = 4
        y = 96
        i_pad = (window.width - 2 * pad - sw) / (num-1)
        self.subs = [_Shield(pad + i_pad*i_x, y)
                     for i_x in range(4)]
    def absorbFromAbove(self, xl, yl, xh, yh):
        return self._absorb(xl, yl, xh, yh, True)
    def absorbFromBelow(self, xl, yl, xh, yh):
        return self._absorb(xl, yl, xh, yh, False)
    def _absorb(self, xl, yl, xh, yh, fromAbove):
        for s in self.subs:
            if s.absorb(xl, yl, xh, yh, fromAbove):
                return self
        return None
    def update(self):
        pass
    def paint(self):
        for s in self.subs:
            s.paint()

class Lives(object):
    PAD_OUTER = 3
    PAD_INNER = 1
    def __init__(self, window):
        self.liferepr = pyglet.resource.image('playerlife.png')
        self.count = 3
        self.x = window.width - (self.PAD_OUTER + self.liferepr.width)
        self.y = window.height - (self.PAD_OUTER + self.liferepr.height)
    def paint(self):
        for i in range(self.count):
            x = self.x - i * (self.PAD_INNER + self.liferepr.width)
            self.liferepr.blit(x, self.y)
    def update(self):
        pass
    def upOne(self):
        self.count += 1
    def loseOne(self):
        self.count -= 1

class Player(object):
    def __init__(self, window, keys):
        self.w = window
        self.k = keys
        self.gun = _Gun(window)
        self.s_alive = _AlivePlayer(window, keys, self.gun)
        self.s_dead = _DeadPlayer()
        self.state = self.s_alive
    def isHit(self, xl, yl, xh, yh):
        if self.state != self.s_alive: return None
        if self.s_alive.isHit(xl, yl, xh, yh):
            self.s_dead.init(self.s_alive.x, self.s_alive.y)
            self.state = self.s_dead
            return self
        return None
    def testGunHit(self, hitFuns):
        self.gun.testHit(hitFuns)
    def update(self):
        self.gun.update()
        if self.state == self.s_dead:
            if not self.state.stillDead:
                self.state = self.s_alive
                self.state.resurrect()
        self.state.update()
    def paint(self):
        self.gun.paint()
        self.state.paint()

class LostPlayer(object):
    def __init__(self, origPlayer):
        if origPlayer.state == origPlayer.s_alive:
            self.state = origPlayer.s_dead
            self.state.init(self.origPlayer.s_alive.x,
                            self.origPlayer.s_alive.y)
        else:
            self.state = origPlayer.s_dead
    def isHit(self, xl, yl, xh, yh):
        return None
    def testGunHit(self, hitFuns):
        pass
    def update(self):
        self.state.update()
    def paint(self):
        self.state.paint()

class _DeadPlayer(object):
    ANIMSPEED = 3
    def __init__(self):
        self.anim = [
            pyglet.resource.image('playermelt01.png'),
            pyglet.resource.image('playermelt02.png'),
            pyglet.resource.image('playermelt03.png'),
            pyglet.resource.image('playermelt04.png'),
            ]
        self.a_tick = 0
        self.a_state = None
        self.stillDead = None
        self.x, self.y = 0, 0
    def init(self, x, y):
        self.x = x
        self.y = y
        self.a_state = 0
        self.stillDead = 30
        self.a_tick = self.ANIMSPEED
    def update(self):
        if self.stillDead: self.stillDead -= 1
        if self.a_state == None: return
        self.a_tick -= 1
        if self.a_tick: return
        self.a_tick = self.ANIMSPEED
        self.a_state += 1
        if self.a_state >= len(self.anim):
            self.a_state = None
            return
    def paint(self):
        if self.a_state == None: return
        self.anim[self.a_state].blit(self.x, self.y)
    
class _AlivePlayer(object):
    def __init__(self, window, keys, gun):
        self.w = window
        self.gun = gun
        self.s = pyglet.resource.image('player.png')
        self.x, self.y = self.w.width/2, 4
        self.keys = keys
        self.invulnerable = 0
    def resurrect(self):
        self.invulnerable = 50
    def update(self):
        if self.invulnerable:
            self.invulnerable -= 1
        vx = 0
        if self.keys[key.LEFT]: vx -= 10
        if self.keys[key.RIGHT]: vx += 10
        self.x += vx
        self.x = max(self.x, 0)
        self.x = min(self.x, self.w.width - self.s.width)
        if self.keys[key.SPACE]: self._pewpew()
    def isHit(self, xl, yl, xh, yh):
        if self.invulnerable: return False
        sxh = self.x+self.s.width
        syh = self.y+self.s.height
        if yl > syh: return False
        if yh < self.y: return False
        if xl > sxh: return False
        if xh < self.x: return False
        return True
    def paint(self):
        if self.invulnerable:
            if (self.invulnerable/5)%2:
                return
        self.s.blit(self.x, self.y)
    def _pewpew(self):
        self.gun.fire(self.x + (self.s.width/2), self.y + self.s.height)

class _Gun(object):
    COOLDOWN_MAX = 5
    def __init__(self, window):
        self.w = window
        self.s = pyglet.resource.image('pewpew.png')
        self.cx, self.cy = self.s.width/2, 0
        self.x, self.y = 0, 0
        self.firing = False
        self.cooldown = 0
    def fire(self, x, y):
        if self.firing: return
        if self.cooldown: return
        self.x = x - self.cx
        self.y = y - self.cy
        self.firing = True
        self.cooldown = self.COOLDOWN_MAX
    def update(self):
        if self.cooldown: self.cooldown -= 1
        if not self.firing: return
        self.y += 15
        if self.y > self.w.height:
            self.firing = False
            return
    def testHit(self, hitFun):
        if not self.firing: return
        if hitFun(self.x, self.y, self.x+self.s.width, self.y+self.s.height):
            self.firing = False
    def paint(self):
        if not self.firing: return
        self.s.blit(self.x, self.y)

class _InvaderExplode(object):
    def __init__(self):
        s = [pyglet.resource.image('invaderexplode0.png'),
             pyglet.resource.image('invaderexplode1.png')]
        self.x, self.y = 0, 0
        self.sm = {'inactive': {'d': 0, 'next': None, 's': None},
                   'explode0': {'d': 5, 'next': 'explode1', 's': s[0]},
                   'explode1': {'d': 10, 'next': 'inactive', 's': s[1]}}
        self.st = 'inactive'
        self.st_c = 0
    def trans(self, state):
        self.st = state
        self.st_c = self.sm[state]['d']
    def boom(self, x, y):
        self.x, self.y = x, y
        self.trans('explode0')
    def paint(self):
        s = self.sm[self.st]['s']
        if not s: return
        s.blit(self.x, self.y)
    def update(self):
        if not self.st_c: return
        self.st_c -= 1
        if self.st_c: return
        self.trans(self.sm[self.st]['next'])

class _InvaderZap(object):
    def __init__(self, window):
        self.w = window
        self.s = pyglet.resource.image('zapzap.png')
        self.cx, self.cy = self.s.width/2, 0
        self.xyl = []
        self.wh = (self.s.width, self.s.height)
    def fire(self, x, y):
        self.xyl.append([x - self.cx, y - self.cy])
    def update(self):
        for p in self.xyl: p[1] -= 10
        self.xyl = [p for p in self.xyl if p[1] > -self.s.height]
    def testHit(self, hitFuns):
        hitItems = []
        xyl2 = []
        for p in self.xyl:
            bounds = p[0], p[1], p[0]+self.s.width, p[1]+self.s.height
            hit = reduce(lambda a, f: a or f(*bounds), hitFuns, None)
            if hit:
                hitItems.append(hit)
                continue # shot absorbed
            xyl2.append(p)
        self.xyl = xyl2
        return hitItems
    def paint(self):
        for [x, y] in self.xyl:
            self.s.blit(x, y)

class Invaders(object):
    def __init__(self, window, diffLevel):
        self.w = window
        self.diffLevel = diffLevel
        self.ROWS = 6
        self.COLS = 8
        self.explode = _InvaderExplode()
        self.zap = _InvaderZap(window)
        self.invader0 = [
            pyglet.resource.image('invader01.png'),
            pyglet.resource.image('invader02.png')]
        self.iw, self.ih = self.invader0[0].width, self.invader0[0].height
        self.pad = 16
        self.x = 2 * self.pad
        self.y = self.w.height - (self.ih + 2 * self.pad)
        self.il = [[True]*self.COLS for _ in [None]*self.ROWS]
        self.bipbop = 0
        self.bipcnt = 0
        self.zapcnt = 100
        self.vx = self.iw/4
        self.vy = -(self.ih + self.pad)
        self.calcWidth()
        self.speed = self.calcSpeed()
        self.moving = True
        
    def calcSpeed(self):
        def getDiffCurve():
            if self.diffLevel > 12:
                return [1, 2,  3,  4,  5,  6,  7]
            if self.diffLevel > 8:
                return [1, 2,  4,  5,  6,  8, 10]
            if self.diffLevel > 6:
                return [2, 4,  5,  6,  8, 10, 13]
            if self.diffLevel > 4:
                return [3, 5,  6,  8, 10, 13, 16]
            if self.diffLevel > 1:
                return [4, 6,  8, 10, 13, 16, 18]
            else:
                return [5, 7, 10, 13, 16, 18, 20]
        speeds = getDiffCurve()
        n = 0
        for r in xrange(self.ROWS):
            for c in xrange(self.COLS):
                if self.il[r][c]:
                    n += 1
        if n < 2:
            return speeds[0]
        if n < 5:
            return speeds[1]
        if n < 10:
            return speeds[2]
        if n < 20:
            return speeds[3]
        if n < 30:
            return speeds[4]
        if n < 40:
            return speeds[5]
        else:
            return speeds[6]

    def collide(self, xl, yl, xh, yh):
        for i_r in xrange(self.ROWS):
            i_yl = self.y - (self.ih + self.pad) * i_r
            i_yh = i_yl + self.ih
            if yh < i_yl: continue
            if yl > i_yh: continue
            for i_c in xrange(self.COLS):
                i_xl = self. x + (self.iw + self.pad) * i_c
                i_xh = i_xl + self.iw
                if xh < i_xl: continue
                if xl > i_xh: continue
                if self.il[i_r][i_c]:
                    self.il[i_r][i_c] = False
                    self.explode.boom(i_xl, i_yl)
                    self.speed = self.calcSpeed()
                    self.reduceSizeIfNeeded()
                    return True
        return False

    def allDead(self):
        return not self.COLS

    def removeZaps(self):
        self.zap = _InvaderZap(self.w)

    def reduceSizeIfNeeded(self):
        for i_c in [0, -1]:
            if not self.COLS: return
            if not sum([self.il[i_r][i_c]
                        for i_r in range(self.ROWS)]):
                self.stripCol(i_c)
                self.reduceSizeIfNeeded()

    def stripCol(self, i_c):
        self.COLS -= 1
        for r in self.il:
            r.pop(i_c)
        if i_c == 0:
            self.x += self.iw + self.pad
        self.calcWidth()

    def calcWidth(self):
        self.totWidth = len(self.il[0]) * (self.iw + self.pad) - self.pad

    def getBottomOfRandomRow(self):
        candidates = []
        for i_c in xrange(self.COLS):
            for i_r in xrange(self.ROWS-1, -1, -1):
                if self.il[i_r][i_c]:
                    candidates.append((i_r, i_c))
                    break
        if not candidates:
            return None, None
        r, c = random.choice(candidates)
        x, y = self.pos(r, c)
        x += self.invader0[0].width / 2
        return x, y

    def update(self):
        self.explode.update()
        self.zap.update()
        self.bipcnt = (self.bipcnt + 1)%self.speed
        if self.bipcnt == 0:
            self.bipbop = (self.bipbop + 1)%2
            if self.moving:
                self.x += self.vx
                if (self.x + self.totWidth > self.w.width) or (self.x < 0):
                    self.vx *= -1
                    self.x += self.vx
                    self.y += self.vy
        self.zapcnt -= 1
        if self.zapcnt == 0:
            self.zapcnt = random.randrange(10, 120)
            x, y = self.getBottomOfRandomRow()
            if x != None:
                self.zap.fire(x, y)

    def pos(self, r, c):
        return (self.x + c*(self.iw + self.pad),
                self.y - r*(self.ih + self.pad))

    def paint(self):
        def paintOne(row, col):
            x, y = self.pos(row, col)
            s = self.invader0[self.bipbop]
            s.blit(x, y)
        self.explode.paint()
        self.zap.paint()
        for ir in xrange(len(self.il)):
            row = self.il[ir]
            for ic in xrange(len(row)):
                row[ic] and paintOne(ir, ic)

GAMEOVER_LABEL = pyglet.text.Label(
    'GAME OVER',
    font_name="sans",
    font_size=24,
    x=0, # set later
    y=0, # set later
    anchor_x="center",
    anchor_y="center") 
class GameOver(object):
    def __init__(self, window):
        self.lbl = GAMEOVER_LABEL
        self.lbl.x = window.width//2
        self.lbl.y = window.height//2
    def update(self):
        pass
    def paint(self):
        self.lbl.draw()

class Level(object):
    def __init__(self, window):
        self.window = window
        self.value = 1
        self.lbl = self.mkLbl()
        self.fullYayWait = 60
        self.done = False
    def mkLbl(self):
        color = (255, 255, 255, 255)
        shinies = '%s'
        if self.value >= 2:
            shinies = shinies%'-%s-'
        if self.value >= 4:
            shinies = shinies%'=%s='
        if self.value >= 6:
            shinies = shinies%'<%s>'
        if self.value >= 8:
            shinies = shinies%'*%s*'
        if self.value >= 10:
            shinies = shinies%'>%s<'
        if self.value >= 12:
            shinies = shinies%'{%s}'
        if self.value >= 14:
            shinies = shinies%'~%s~'
        if self.value >= 16:
            shinies = shinies%'_%s_'
        if self.value >= 18:
            shinies = shinies%'/%s\\'
        if self.value >= 20:
            shinies = shinies%' %s '
            color = (238, 201, 0, 255) # gold!
        return pyglet.text.Label(
            shinies%('LEVEL %d'%self.value),
            font_name="sans",
            font_size=15,
            x=self.window.width // 2,
            y=self.window.height,
            anchor_x="center",
            anchor_y="top",
            color=color)
    def up(self):
        self.value += 1
        self.lbl = self.mkLbl()
    def update(self):
        pass
    def paint(self):
        self.lbl.draw()

def _mkYayLbl(level):
    return pyglet.text.Label(
        'YOU BEAT LEVEL %d'%level,
        font_name="sans",
        font_size=50,
        x=0, # window.width // 2 later
        y=0, # window.height // 2 later
        anchor_x="center",
        anchor_y="center")
_YAY_LABELS = [_mkYayLbl(n) for n in xrange(20)]
class YayYou(object):
    def __init__(self, window, level):
        global _YAY_LABELS
        while level >= len(_YAY_LABELS):
            _YAY_LABELS.extend([_mkYayLbl(n) for n in xrange(len(_YAY_LABELS), len(_YAY_LABELS)+10)])
        self.lbl = _YAY_LABELS[level]
        self.lbl.x = window.width // 2
        self.lbl.y = window.height // 2
        self.countdown = 60
        self.halfcountdown = self.countdown // 2
        self.done = False
        self.halfDone = False
    def update(self):
        if self.countdown:
            self.countdown -= 1
        self.halfDone = self.countdown > self.halfcountdown
        self.done = not self.countdown
    def paint(self):
        self.lbl.draw()
