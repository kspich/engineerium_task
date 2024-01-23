import pygame
import random
from pygame.locals import *

import Game as g
from EnemyBullet import EnemyBullet

class Enemy(pygame.sprite.Sprite):
        def __init__(self, x ,y, game):
            super().__init__()
            self.env = game
            self.surf = pygame.Surface((50, 50))
            self.surf.fill((255,0,0))
            self.rect = self.surf.get_rect(center = (x, y))
            self.counter = 0
            self.firerate = random.uniform(60, 120)
        def shoot(self):
            if (self.counter > self.firerate):
                coords = list(self.rect.center)
                coords[1] += 25
                self.env.bullets.add(EnemyBullet(*coords))
                self.counter = 0
            else: 
                self.counter+=1
        def collide(self): return pygame.sprite.spritecollide(self , self.env.player_bullets, True)
        def update(self):
            hits = self.collide()
            if hits:
                self.kill()
                self.env.score += (3600-self.env.counter)//60
                print(self.env.score)