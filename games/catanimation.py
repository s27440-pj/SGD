import pygame, sys
from pygame.locals import *

pygame.init()

FPS = 30 # frames per second setting
fpsClock = pygame.time.Clock()

# set up the window
DISPLAYSURF = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption('Animation')

WHITE = (255, 255, 255)
catImg = pygame.image.load('cat.png')
catx = 10
caty = 10
direction = 'right'
catImg2 = pygame.image.load('pepe.png')
pepex = 260
pepey = 10
direction_pepe = 'left'


while True: # the main game loop
    DISPLAYSURF.fill(WHITE)

    if direction == 'right':
        catx += 5
        if catx == 280:
            direction = 'down'
    elif direction == 'down':
        caty += 5
        if caty == 220:
            direction = 'left'
    elif direction == 'left':
        catx -= 5
        if catx == 10:
            direction = 'up'
    elif direction == 'up':
        caty -= 5
        if caty == 10:
            direction = 'right'

    if direction_pepe == 'left':
        pepex -= 5
        if pepex == 10:
            direction_pepe = 'down'
    elif direction_pepe == 'down':
        pepey += 5
        if pepey == 140:
            direction_pepe = 'right'
    elif direction_pepe == 'right':
        pepex += 5
        if pepex == 270:
            direction_pepe = 'up'
    elif direction_pepe == 'up':
        pepey -= 5
        if pepey == 10:
            direction_pepe = 'left'

    DISPLAYSURF.blit(catImg, (catx, caty))
    DISPLAYSURF.blit(catImg2, (pepex, pepey))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fpsClock.tick(FPS)