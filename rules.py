class Rules:
    def __init__(self, player, playerZap, shields):
        self.p = player
        self.pz = playerZap
        self.s = shields

    def tick(self):
        pzb = self.pz.bounds()
        if not pzb:
            return
        if self.s.absorb(pzb, fromAbove=False):
            self.pz.die()
