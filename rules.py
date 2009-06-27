from sprites import Player, LostPlayer, Invaders, Shields, Lives, GameOver, YayYou, Level

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
        if prevStuff:
            self.s = prevStuff
        else:
            self.s = {
                'shields': Shields(self.window),
                'player': Player(self.window, self.keys),
                'lives': Lives(self.window),
                'level': Level(self.window),
                }
        self.s['invaders'] = Invaders(self.window, self.s['level'].value)
        self.paintOrder = self.s.values()
        # move level to end of order - yes, it works
        self.paintOrder.append(self.s['level'])
        self.paintOrder.remove(self.s['level'])
    def update(self):
        for s in self.s.values(): s.update()
        runHitTests(self.s)
        if self.s['lives'].count < 0:
            return self.goto(StateLose, self.s)
        if self.s['invaders'].allDead():
            return self.goto(StateNextLevel, self.s)
        return self
    def visibleStuff(self):
        return self.paintOrder

class StateNextLevel(State):
    def postInit(self, prevStuff):
        self.s = prevStuff
        self.s['invaders'].removeZaps()
        self.yay = YayYou(self.window, self. s['level'].value)
        self.s['level'].up()
        self.livesUpped = False
    def update(self):
        self.yay.update()
        self.s['invaders'].update()
        if self.yay.halfDone and not self.livesUpped:
            self.s['lives'].upOne()
            self.livesUpped = True
        if self.yay.done:
            return self.goto(StatePlay, self.s)
        return self
    def visibleStuff(self):
        return self.s.values() + [self.yay]

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
