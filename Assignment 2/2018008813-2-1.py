import glfw
from OpenGL.GL import *
import numpy as np

global PrimitiveTypeDictionary
global PrimitiveTypeKey

PrimitiveTypeKey = glfw.KEY_4
PrimitiveTypeDictionary = dict()
PrimitiveTypeDictionary[glfw.KEY_1] = GL_POINTS
PrimitiveTypeDictionary[glfw.KEY_2] = GL_LINES
PrimitiveTypeDictionary[glfw.KEY_3] = GL_LINE_STRIP
PrimitiveTypeDictionary[glfw.KEY_4] = GL_LINE_LOOP
PrimitiveTypeDictionary[glfw.KEY_5] = GL_TRIANGLES
PrimitiveTypeDictionary[glfw.KEY_6] = GL_TRIANGLE_STRIP
PrimitiveTypeDictionary[glfw.KEY_7] = GL_TRIANGLE_FAN
PrimitiveTypeDictionary[glfw.KEY_8] = GL_QUADS
PrimitiveTypeDictionary[glfw.KEY_9] = GL_QUAD_STRIP
PrimitiveTypeDictionary[glfw.KEY_0] = GL_POLYGON

def render():
    global PrimitiveTypeDictionary
    global PrimitiveTypeKey

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(PrimitiveTypeDictionary[PrimitiveTypeKey])

    angle = np.arange(0, 360, 30)
    for i in angle:
        glVertex2f(np.cos(i*np.pi/180), np.sin(i*np.pi/180))

    glEnd()


def call(window, key, scancode, action, mods):
    global PrimitiveTypeDictionary
    global PrimitiveTypeKey

    if action == glfw.PRESS:
        PrimitiveTypeKey = key
    

def main():
    if not glfw.init():
        return
    
    window =  glfw.create_window(480,480,"2018008813-2-1",None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, call)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

        
