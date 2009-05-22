import sys

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

DEBUGCOUNT = 300
def profileRun(dt):
    global DEBUGCOUNT
    if not DEBUGCOUNT:
        pyglet.app.exit()
    DEBUGCOUNT -= 1
    return normalRun(dt)
    
def normalRun(dt):
    for s in STUFF: s.update()
    rules.tick()

profileMode = (sys.argv+[0])[1] == 'debug'

if profileMode:
    pyglet.clock.set_fps_limit(1000)
    pyglet.clock.schedule(profileRun)
    import cProfile
    cProfile.run('pyglet.app.run()', sort=1) # sort by tottime
else:
    pyglet.clock.set_fps_limit(50)
    pyglet.clock.schedule(normalRun)
    pyglet.app.run()
