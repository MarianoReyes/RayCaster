import pygame
from OpenGL.GL import *
import copy

pygame.init()

scale = 10

screen = pygame.display.set_mode(
    (100*scale, 100*scale),
    pygame.OPENGL | pygame.DOUBLEBUF
)


def pixel(x, y, color):
    glEnable(GL_SCISSOR_TEST)
    glScissor(x*scale, y*scale, 1*scale, 1*scale)
    glClearColor(color[0], color[1], color[2], 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glDisable(GL_SCISSOR_TEST)


x = 1
y = 1

size = 100

framebuffer = []

for x in range(1, size+1):
    mm = []
    for y in range(1, size+1):
        xy = 0
        mm.append(xy)
        # print(xy)
        y = +1
    framebuffer.append(mm)
    x = +1


def check_vecinos(x, y, framebuffer):
    contador = 0
    # checkear todos los pixeles aalrededor de una celula
    if x > 0 and x < 99 and y > 0 and y < 99:
        if framebuffer[x-1][y+1] == 1:
            contador += 1
        if framebuffer[x][y+1] == 1:
            contador += 1
        if framebuffer[x+1][y+1] == 1:
            contador += 1
        if framebuffer[x-1][y] == 1:
            contador += 1
        if framebuffer[x+1][y] == 1:
            contador += 1
        if framebuffer[x-1][y-1] == 1:
            contador += 1
        if framebuffer[x][y-1] == 1:
            contador += 1
        if framebuffer[x+1][y-1] == 1:
            contador += 1

    return contador


def draw():
    for x in range(len(framebuffer)):
        for y in range(len(framebuffer)):
            if framebuffer[x][y] == 1:
                pixel(x, y, (1, 1, 1))
            else:
                pixel(x, y, (0, 0, 0))


def turn():
    # funcion que simula el turno
    old = copy.deepcopy(framebuffer)
    for x in range(size):
        for y in range(size):
            # regla 1
            if framebuffer[x][y] == 1:
                if check_vecinos(x, y, old) < 2:
                    framebuffer[x][y] = 0
                # regla 3
                if check_vecinos(x, y, old) > 3:
                    framebuffer[x][y] = 0
                # regla 2
                if check_vecinos(x, y, old) == 2 or check_vecinos(x, y, old) == 3:
                    framebuffer[x][y] = 1

            else:
                if check_vecinos(x, y, old) == 3:
                    framebuffer[x][y] = 1
    draw()


y = 50

# config inicial

# Inicio glider gun
framebuffer[9][y+10] = 1
framebuffer[9][y+11] = 1
framebuffer[10][y+10] = 1
framebuffer[10][y+11] = 1

framebuffer[19][y+10] = 1
framebuffer[19][y+11] = 1
framebuffer[19][y+12] = 1
framebuffer[20][y+9] = 1
framebuffer[21][y+8] = 1
framebuffer[22][y+8] = 1
framebuffer[20][y+13] = 1
framebuffer[21][y+14] = 1
framebuffer[22][y+14] = 1

framebuffer[23][y+11] = 1

framebuffer[25][y+11] = 1
framebuffer[26][y+11] = 1
framebuffer[25][y+10] = 1
framebuffer[25][y+12] = 1
framebuffer[24][y+9] = 1
framebuffer[24][y+13] = 1

framebuffer[29][y+12] = 1
framebuffer[29][y+13] = 1
framebuffer[29][y+14] = 1
framebuffer[30][y+12] = 1
framebuffer[30][y+13] = 1
framebuffer[30][y+14] = 1

framebuffer[31][y+15] = 1
framebuffer[31][y+11] = 1
framebuffer[33][y+11] = 1
framebuffer[33][y+10] = 1
framebuffer[33][y+15] = 1
framebuffer[33][y+16] = 1

framebuffer[43][y+14] = 1
framebuffer[43][y+13] = 1
framebuffer[44][y+14] = 1
framebuffer[44][y+13] = 1
# final glider gun

running = True
while running:
    # clean
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    # paint
    turn()
    # flip
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
