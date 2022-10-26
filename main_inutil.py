from cyglfw3 as glfw
from OpenGL.GL import *

glfw.Init()

window = glfw.CreateWindow(800,800, 'opengl')

while not glfw,WindowsShouldClose(window):
    glfw.PollEvents()

glfw.Terminate()