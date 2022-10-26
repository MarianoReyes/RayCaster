import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))

x = 10
y = 10

running = True
while running:
    # clean

    # paint
    screen.set_at((x, y), (255, 255, 255))
    x += 1
    y += 1
    # flip
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
