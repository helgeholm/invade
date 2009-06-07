import sys

import pyglet
from pyglet.window import key

from rules import StatePlay

window = pyglet.window.Window(1024, 768)
keys = key.KeyStateHandler()
window.push_handlers(keys)

#music = pyglet.resource.media('Hazel - Mip Mip Police.mp3')
#music.play()

state = StatePlay(window, keys)

@window.event
def on_draw():
    global state
    window.clear()
    for s in state.visibleStuff():
        if not hasattr(s, 'paint'):
            raise Exception('Got unpaintable object "%s" from visibleStuff from state %s.'%(repr(s), repr(state)))
        s.paint()

timeacc = 0
INTV = 0.02
def normalRun(dt):
    global state
    global timeacc
    timeacc += dt
    if timeacc > INTV:
        nextState = state.update()
        if not nextState:
            raise Exception('State "%s" returned bad new state %s.'%(state, nextState))
        state = nextState
    while timeacc > INTV:
        timeacc -= INTV

DEBUGCOUNT = 300
def profileRun(dt):
    global DEBUGCOUNT
    if not DEBUGCOUNT:
        pyglet.app.exit()
    DEBUGCOUNT -= 1
    return normalRun(dt)

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
