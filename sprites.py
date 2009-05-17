import random

import pyglet
from pyglet.window import key

class Player(object):
    def __init__(self, window, gun):
        self.w = window
        self.g = gun
        self.s = pyglet.resource.image('player.png')
        self.x, self.y = self.w.width/2, 4
    def update(self, keys):
        vx = 0
        if keys[key.LEFT]: vx -= 10
        if keys[key.RIGHT]: vx += 10
        self.x += vx
        self.x = max(self.x, 0)
        self.x = min(self.x, self.w.width - self.s.width)
        if keys[key.SPACE]: self._pewpew()
    def paint(self):
        self.s.blit(self.x, self.y)
    def _pewpew(self):
        self.g.fire(self.x + (self.s.width/2), self.y + self.s.height)

class Gun(object):
    def __init__(self, window, invaders):
        self.w = window
        self.i = invaders
        self.s = pyglet.resource.image('pewpew.png')
        self.cx, self.cy = self.s.width/2, 0
        self.x, self.y = 0, 0
        self.firing = False
    def fire(self, x, y):
        if self.firing: return
        self.x = x - self.cx
        self.y = y - self.cy
        self.firing = True
    def update(self, keys):
        if not self.firing: return
        self.y += 15
        if self.y > self.w.height:
            self.firing = False
            return
        if self.i.collide(self.x, self.y, self.s.width, self.s.height):
            self.firing = False
    def paint(self):
        if not self.firing: return
        self.s.blit(self.x, self.y)

class InvaderExplode(object):
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
    def update(self, keys):
        if not self.st_c: return
        self.st_c -= 1
        if self.st_c: return
        self.trans(self.sm[self.st]['next'])

class InvaderZap(object):
    def __init__(self, window):
        self.w = window
        self.s = pyglet.resource.image('zapzap.png')
        self.cx, self.cy = self.s.width/2, 0
        self.xyl = []
    def fire(self, x, y):
        self.xyl.append([x - self.cx, y - self.cy])
    def update(self, keys):
        xyl2 = []
        for p in self.xyl:
            p[1] -= 10
            if p[1] > 0:
                xyl2.append(p)
        self.xyl = xyl2
    def paint(self):
        for [x, y] in self.xyl:
            self.s.blit(x, y)

class Invaders(object):
    def __init__(self, window, zap, invadersExp):
        self.explode = invadersExp
        self.ROWS = 6
        self.COLS = 8
        self.zap = zap
        self.w = window
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
        self.vy = -self.ih
        self.calcWidth()

    def collide(self, xl, yl, w, h):
        xh, yh = xl + w, yl + h
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
                    self.reduceSizeIfNeeded()
                    return True
        return False

    def reduceSizeIfNeeded(self):
        if not self.COLS: return
        for i_c in [0, -1]:
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

    def update(self, keys):
        self.bipcnt = (self.bipcnt + 1)%20
        if self.bipcnt == 0:
            self.bipbop = (self.bipbop + 1)%2
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
        for ir in xrange(len(self.il)):
            row = self.il[ir]
            for ic in xrange(len(row)):
                row[ic] and paintOne(ir, ic)