import pyglet
from pyglet.window import key

from sprites import Player, Invaders, Shields
from rules import Rules

window = pyglet.window.Window(1024, 768)
keys = key.KeyStateHandler()
window.push_handlers(keys)

#music = pyglet.resource.media('Hazel - Mip Mip Police.mp3')
#music.play()

shields = Shields(window)
invaders = Invaders(window)
player = Player(window, keys)
rules = Rules(player, player.gun, shields, invaders, invaders.zap)
STUFF = [invaders, player, shields]

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
        rules.tick()
    while timeacc > INTV:
        timeacc -= INTV
    

pyglet.clock.schedule(update)

pyglet.app.run()
