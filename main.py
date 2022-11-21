import pygame
import random
from math import cos, sin, pi, atan2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)

SKY = (150, 147, 135)
GROUND = (168, 114, 67)

colors = [
    (0, 20, 10),
    (4, 40, 63),
    (0, 91, 82),
    (219, 242, 38),
    (21, 42, 138)
]

walls = {
    "1": pygame.image.load('./wallc1.jpg'),
    "2": pygame.image.load('./wallc2.jpg'),
    "3": pygame.image.load('./wallc3.jpg'),
}

sprites = [
    {
        "x": 205,
        "y": 395,
        "texture": pygame.image.load('./cofre.png'),
        "picked": False
    },
    {
        "x": 305,
        "y": 395,
        "texture": pygame.image.load('./cofre.png'),
        "picked": False
    },
    {
        "x": 405,
        "y": 395,
        "texture": pygame.image.load('./cofre.png'),
        "picked": False
    },
    {
        "x": 405,
        "y": 105,
        "texture": pygame.image.load('./cofre.png'),
        "picked": False
    },
]


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()
        self.blocksize = 50
        self.map = []
        self.zbuffer = [-float('inf') for z in range(0, 500)]
        self.player = {
            "x": self.blocksize + self.blocksize / 2,
            "y": self.blocksize + self.blocksize / 2,
            "fov": int(pi/3),
            "a": int(pi/3),
            "wincondition": 0
        }
        self.movimiento = ""

    def point(self, x, y, c=WHITE):
        # colocar pixel de game of life
        self.screen.set_at((x, y), c)

    def block(self, x, y, wall):
        for i in range(x, x+self.blocksize):
            for j in range(y, y+self.blocksize):
                tx = int((i-x) * 128 / self.blocksize)
                ty = int((j-y) * 128 / self.blocksize)
                c = wall.get_at((tx, ty))
                self.point(i, j, c)

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def draw_stake(self, x, h, tx, c):
        start_y = int(self.height/2 - h/2)
        end_y = int(self.height/2 + h/2)

        height = end_y - start_y

        for y in range(start_y, end_y):
            ty = int((y-start_y) * 128 / height)
            color = walls[c].get_at((tx, ty))
            self.point(x, y, color)

    def cast_ray(self, a):
        d = 0
        ox = self.player["x"]
        oy = self.player["y"]

        while True:
            x = int(ox + d*cos(a))
            y = int(oy + d*sin(a))

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if self.map[j][i] != ' ':
                hitx = x-i*self.blocksize
                hity = y-j*self.blocksize

                if 1 < hitx < self.blocksize-1:
                    maxhit = hitx
                else:
                    maxhit = hity

                tx = int(maxhit * 128 / self.blocksize)
                return d, self.map[j][i], tx

            self.point(x, y)
            d += 5

    def draw_map(self):
        for x in range(0, 500, self.blocksize):
            for y in range(0, 500, self.blocksize):
                i = int(x/self.blocksize)
                j = int(y/self.blocksize)
                if self.map[j][i] != ' ':
                    self.block(x, y, walls[self.map[j][i]])

    def draw_player(self):
        self.point(int(self.player["x"]), int(self.player["y"]))

    def draw_sprite(self, sprite):

        sprite_d = ((self.player["x"] - sprite["x"]) **
                    2 + (self.player["y"] - sprite["y"])**2)**0.5

        if sprite_d != 0 and sprite["picked"] == False:

            sprite_a = atan2(sprite["y"] - self.player["y"],
                             sprite["x"] - self.player["x"])

            sprite_size = (500/sprite_d) * 30

            sprite_x = 500 + \
                (sprite_a - self.player["a"])*500 / \
                self.player["fov"] + 250 - sprite_size/2
            sprite_y = 250 - sprite_size/2

            sprite_x = int(sprite_x)
            sprite_y = int(sprite_y)
            sprite_size = int(sprite_size)

            for x in range(sprite_x, sprite_x + sprite_size):
                for y in range(sprite_y, sprite_y + sprite_size):
                    if 500 < x < 1000 and self.zbuffer[x - 500] >= sprite_d:
                        tx = int((x - sprite_x) * 128/sprite_size)
                        ty = int((y - sprite_y) * 128/sprite_size)
                        c = sprite["texture"].get_at((tx, ty))
                        if c != (0, 0, 0, 0):
                            self.point(x, y, c)
                            self.zbuffer[x - 500] = sprite_d

    # funcion creada por si chica con pared
    def goback(self):
        if self.movimiento == "izquierda":
            self.player["y"] += 10
        elif self.movimiento == "derecha":
            self.player["y"] -= 10
        elif self.movimiento == "arriba":
            self.player["x"] -= 10
        elif self.movimiento == "abajo":
            self.player["x"] += 10

    def comprobar(self):
        for sprite in sprites:
            if sprite["picked"] == False:
                print("posición del cofre ",
                      sprite["x"], sprite["y"])
                if int(sprite["x"]) == int(self.player["x"]) and int(sprite["y"]) == int(self.player["y"]):
                    sprite["picked"] = True
                    pygame.mixer.Channel(1).play(
                        pygame.mixer.Sound('pick.wav'))
                    self.player["wincondition"] += 1
        print("posición del jugador", int(
            self.player["x"]), int(self.player["y"]))

    def render(self):
        self.draw_map()
        self.draw_player()

        density = 40

        # minimap
        for i in range(0, density):
            a = self.player["a"] - self.player["fov"] / \
                2 + self.player["fov"]*i/density
            d, c, _ = self.cast_ray(a)

        # separador
        for i in range(0, 500):
            self.point(499, i)
            self.point(500, i)
            self.point(501, i)

        # draw in 3d
        try:
            for i in range(0, int(self.width/2)):
                a = self.player["a"] - self.player["fov"] / \
                    2 + self.player["fov"]*i/(self.width/2)
                d, c, tx = self.cast_ray(a)

                x = int(self.width/2 + i)

                h = self.height/(d * cos(a-self.player["a"])) * 100

                self.draw_stake(x, h, tx, c)
                self.zbuffer[i] = d
        except:
            print("Hay una pared ahí...")
            self.goback()

        for sprite in sprites:
            if sprite["picked"] == False:
                self.point(sprite["x"], sprite["y"], (0, 0, 0))
                self.draw_sprite(sprite)


#pygame.mixer.pre_init(44100, -16, 1, 512)

pygame.init()
# screen = pygame.display.set_mode((1000, 500), pygame.FULLSCREEN)
screen = pygame.display.set_mode((1000, 500))
r = Raycaster(screen)

pygame.mixer.init()
sonido_fondo = pygame.mixer.Sound("musica_nivel1.mp3")


pygame.display.set_caption('Get Chests')

font = pygame.font.Font('freesansbold.ttf', 32)

clock = pygame.time.Clock()

inicio = pygame.image.load('./pantalla_inicio.jpg')

pygame.mixer.Channel(0).play(pygame.mixer.Sound('musica_nivel1.mp3'))


running = True
while running:

    for x in range(0, 512):
        for y in range(0, 512):
            color = inicio.get_at((x, y))
            r.point(x, y, color)

    pygame.display.flip()
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_1):
                level = 1
                running = False
            if (event.key == pygame.K_2):
                level = 2
                running = False
            if (event.key == pygame.K_3):
                level = 3
                running = False
if level == 1:
    r.load_map("./map1.txt")
elif level == 2:
    r.load_map("./map2.txt")
elif level == 3:
    r.load_map("./map3.txt")

running = True
while running:

    clock.tick()
    fps = clock.get_fps()
    fps = str(round(fps, 2)) + " fps ... "
    wincond = str(r.player["wincondition"])
    wincond = wincond + " cofres recogidos"

    todo = fps + wincond
    level_info = font.render(todo, True, WHITE, BLACK)

    screen.fill(BLACK, (0, 0, r.width/2, r.width/2))
    screen.fill(SKY, (r.width/2, 0, r.width, r.height/2))
    screen.fill(GROUND, (r.width/2, r.height/2, r.width, r.height/2))
    r.render()

    screen.blit(level_info, (r.width - 480, r.height - 50))

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # movimiento de camara con ruedita de mouse
        if event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                r.player["a"] += pi/10
            elif event.y == -1:
                r.player["a"] -= pi/10

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                r.movimiento = "arriba"
                r.player["x"] += 10
            if event.key == pygame.K_DOWN:
                r.movimiento = "abajo"
                r.player["x"] -= 10
            if event.key == pygame.K_LEFT:
                r.movimiento = "izquierda"
                r.player["y"] -= 10
            if event.key == pygame.K_RIGHT:
                r.movimiento = "derecha"
                r.player["y"] += 10

            if event.key == pygame.K_w:
                r.movimiento = "arriba"
                r.player["x"] += 10
            if event.key == pygame.K_s:
                r.movimiento = "abajo"
                r.player["x"] -= 10
            if event.key == pygame.K_a:
                r.movimiento = "izquierda"
                r.player["y"] -= 10
            if event.key == pygame.K_d:
                r.movimiento = "derecha"
                r.player["y"] += 10

        r.comprobar()

        if r.player["wincondition"] == 4:
            running = False

final = pygame.image.load('./pantalla_fin.jpg')

if r.player["wincondition"] == 4:
    running = True
    while running:
        screen.fill(BLACK, (0, 0, r.width, r.height))
        for x in range(0, 512):
            for y in range(0, 512):
                color = final.get_at((x, y))
                r.point(x, y, color)

        pygame.display.flip()
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if (event.type == pygame.KEYDOWN):
                if event.key == pygame.K_KP_ENTER:
                    running = False
