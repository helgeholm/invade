import pyglet
from pyglet.window import key

from sprites import Player, Gun, Invaders, InvaderExplode, InvaderZap

window = pyglet.window.Window(1024, 768)
keys = key.KeyStateHandler()
window.push_handlers(keys)

#music = pyglet.resource.media('Hazel - Mip Mip Police.mp3')
#music.play()

zap = InvaderZap(window)
invadersExp = InvaderExplode()
invaders = Invaders(window, zap, invadersExp)
gun = Gun(window, invaders)
player = Player(window, gun, keys)
STUFF = [zap, invadersExp, invaders, gun, player]

@window.event
def on_draw():
    window.clear()
    for s in STUFF: s.paint()

timeacc = 0
INTV = 0.02
def update(dt):
    global timeacc
    timeacc += dt
    if timeacc > INTV:
        for s in STUFF: s.update()
    while timeacc > INTV:
        timeacc -= INTV
    

pyglet.clock.schedule(update)

pyglet.app.run()
