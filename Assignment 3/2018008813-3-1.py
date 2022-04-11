import glfw
from OpenGL.GL import *
import numpy as np

gComposedM = np.identity(3)

def render(T):
    global gComposedM
    
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv( (T @ np.array([.0,.5,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.0,.0,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.5,.0,1.]))[:-1] )
    glEnd()

def call(window, key, scancode, action, mods):
    global gComposedM
    
    Q = np.array([[1, 0, -0.1],
                 [0, 1, 0],
                 [0, 0, 1]])
    E = np.array([[1, 0, 0.1],
                 [0, 1, 0],
                 [0, 0, 1]])
    A = np.array([[np.cos(np.pi/18), -np.sin(np.pi/18), 0],
                 [np.sin(np.pi/18), np.cos(np.pi/18), 0],
                 [0, 0, 1]])
    D = np.array([[np.cos(-np.pi/18), -np.sin(-np.pi/18), 0],
                 [np.sin(-np.pi/18), np.cos(-np.pi/18), 0],
                 [0, 0, 1]])
    W = np.array([[0.9, 0, 0],
                 [0, 1, 0],
                 [0, 0, 1]])
    S = np.array([[np.cos(np.pi/18), -np.sin(np.pi/18), 0],
                 [np.sin(np.pi/18), np.cos(np.pi/18), 0],
                 [0, 0, 1]])
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_Q:
            gComposedM = Q @ gComposedM
        elif key == glfw.KEY_E:
            gComposedM = E @ gComposedM
        elif key == glfw.KEY_A:
            gComposedM = gComposedM @ A
        elif key == glfw.KEY_D:
            gComposedM = gComposedM @ D
        elif key == glfw.KEY_1:
            gComposedM = np.identity(3)
        elif key == glfw.KEY_W:
            gComposedM = W @ gComposedM
        elif key == glfw.KEY_S:
            gComposedM = S @ gComposedM

def main():
    if not glfw.init():
        return
    
    window =  glfw.create_window(480,480,"2018008813-3-1",None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, call)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        render(gComposedM)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

        
