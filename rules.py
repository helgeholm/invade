class Rules:
    def __init__(self, player, playerZap, shields, invaders, invadersZap):
        self.p = player
        self.pz = playerZap
        self.s = shields
        self.i = invaders
        self.iz = invadersZap

    def tick(self):
        # player gun hit
        self.pz.testHit(self.s.absorbFromBelow)
        self.pz.testHit(self.i.collide)
        self.iz.testHit([self.s.absorbFromAbove])
