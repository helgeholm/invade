from sprites import Player, LostPlayer, Invaders, Shields, Lives, GameOver

class State(object):
    def __init__(self, window, keys, prevState=None):
        self.window = window
        self.keys = keys
        self.postInit(prevState)
    def goto(self, newStateClass, passStuff):
        return newStateClass(self.window, self.keys, passStuff)

def runHitTests(s):
    s['player'].testGunHit(s['shields'].absorbFromBelow)
    s['player'].testGunHit(s['invaders'].collide)
    hit = s['invaders'].zap.testHit(
        [s['shields'].absorbFromAbove, s['player'].isHit])
    if s['player'] in hit:
        s['lives'].loseOne()

class StatePlay(State):
    def postInit(self, prevStuff):
        self.s = {
            'shields': Shields(self.window),
            'invaders': Invaders(self.window),
            'player': Player(self.window, self.keys),
            'lives': Lives(self.window),
            }
    def update(self):
        for s in self.s.values(): s.update()
        runHitTests(self.s)
        if self.s['lives'].count < 0:
            return self.goto(StateLose, self.s)
        return self
    def visibleStuff(self):
        return self.s.values()

class StateLose(State):
    def postInit(self, prevStuff):
        self.s = prevStuff
        self.s['player'] = LostPlayer(self.s['player'])
        self.s['invaders'].moving = False
        self.paintOrder = self.s.values()
        self.s['gameover'] = GameOver(self.window)
        self.paintOrder.append(self.s['gameover'])
    def update(self):
        for s in self.s.values(): s.update()
        runHitTests(self.s)
        return self
    def visibleStuff(self):
        return self.paintOrder
