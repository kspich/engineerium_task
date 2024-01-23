import pygame
from pygame.locals import *

import Game as g
from PlayerBullet import PlayerBullet

class Player(pygame.sprite.Sprite):
        def __init__(self, game):
            super().__init__()
            self.env = game
            self.surf = pygame.Surface((50, 50))
            self.surf.fill((128,255,40))
            self.rect = self.surf.get_rect()
            self.pos = g.vec((400, 580))
            self.vel = g.vec(0,0)
            self.acc = g.vec(0,0)
            self.counter = 0
            self.firerate = 20
            self.name = ''

        def shoot(self):
            coords = list(self.rect.center)
            coords[1] -= 15
            self.env.player_bullets.add(PlayerBullet(*coords))
            self.counter = 0

        def move(self):
            self.acc = g.vec(0,0)
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_LEFT]:
                self.acc.x = -g.ACC
            if pressed_keys[K_RIGHT]:
                self.acc.x = g.ACC
            self.acc.x += self.vel.x * g.FRIC
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc

            if self.pos.x > g.WIDTH:
                self.pos.x = 0
            if self.pos.x < 0:
                self.pos.x = g.WIDTH
            self.rect.midbottom = self.pos

        def collide(self): return pygame.sprite.spritecollide(self, self.env.bullets, True)
        def update(self):
            hits = self.collide()
            return hits