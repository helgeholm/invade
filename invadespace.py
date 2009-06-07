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
    for s in state.visibleStuff(): s.paint()

timeacc = 0
INTV = 0.02
def update(dt):
    global state
    global timeacc
    timeacc += dt
    if timeacc > INTV:
        state = state.update()
    while timeacc > INTV:
        timeacc -= INTV
    

pyglet.clock.schedule(update)

pyglet.app.run()
