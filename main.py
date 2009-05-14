import pyglet
from pyglet.window import mouse

window = pyglet.window.Window()

image = pyglet.resource.image('jagers.jpg')

label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

music = pyglet.resource.media('Hazel - Mip Mip Police.mp3')
music.play()

ix, iy = 0, 0

@window.event
def on_draw():
    window.clear()
    image.blit(ix, iy)
    label.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global ix, iy
    if button == mouse.LEFT:
        ix, iy = x, y
    

pyglet.app.run()
