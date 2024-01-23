import pygame
from pygame.locals import *

import Game as g

class EnemyBullet(pygame.sprite.Sprite):
        def __init__(self, x ,y):
            super().__init__()
            self.surf = pygame.Surface((12, 20))
            self.surf.fill((255,0,0))
            self.rect = self.surf.get_rect(center = (x, y))
        def move(self):
            coords = list(self.rect.center)
            if (coords[1] > g.HEIGHT): 
                self.kill()
                return
            coords[1] += 10
            self.rect = self.surf.get_rect(center = (coords[0], coords[1]))