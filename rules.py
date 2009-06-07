class Rules:
    def __init__(self, player, playerZap, shields, invaders, invadersZap, playerLives):
        self.p = player
        self.pz = playerZap
        self.pl = playerLives
        self.s = shields
        self.i = invaders
        self.iz = invadersZap

    def tick(self):
        self.pz.testHit(self.s.absorbFromBelow)
        self.pz.testHit(self.i.collide)
        hit = self.iz.testHit([self.s.absorbFromAbove, self.p.isHit])
        if self.p in hit:
            self.pl.loseOne()
