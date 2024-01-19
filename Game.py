import pygame
from pygame.locals import *
import sys
import random
import InputBox
import sqlite3

pygame.init()
pygame.font.init()

font = pygame.font.SysFont('Arial', 40)
vec = pygame.math.Vector2

WIDTH, HEIGHT = 800, 600
ACC = 0.7
FRIC = -0.12
FPS = 60

FramePerSec = pygame.time.Clock()
pygame.display.set_caption("Game")

def blitMultiline(surface, text, pos, font, color):
    words = [word.split(' ') for word in text.splitlines()]
    space = font.size(' ')[0]
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]
                y += word_height
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]
        y += word_height

class Game:
    def __init__(self) -> None:
        self.pause_text_surface = font.render('Click the box below and type the name', False, (255,255,255))
        self.PAUSE = True
        self.WIN = False
        self.LOSE = False
        self.display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.enemies = pygame.sprite.Group()
        self.enemies.add(self.Enemy(WIDTH/2, 50, self))
        dumb_flag = True
        for x in range(WIDTH//2, WIDTH - 10, WIDTH//11):
            if dumb_flag: 
                dumb_flag = not dumb_flag
                continue
            self.enemies.add(self.Enemy(x, 50, self))
            self.enemies.add(self.Enemy(WIDTH//2 - (x - WIDTH//2), 50, self))
        self.P1 = self.Player(self)
        self.player_bullets = pygame.sprite.Group() 
        self.bullets = pygame.sprite.Group()
        self.input_box = InputBox.InputBox(20, 80, 300, 60, 'Player')
        self.highscores = self.HighScores()
        self.counter = 0
        self.score = 0

    class HighScores():
        def __init__(self) -> None:
            self.db = sqlite3.connect("players.db")
            self.cur = self.db.cursor()
            self.cur.execute("CREATE TABLE IF NOT EXISTS players(name, score)")
            print(f'Database was initialized')

        def pasteNew(self, name, score):
            self.cur.execute(f"INSERT INTO players VALUES ('{name}', {score})")
            print(f'New score ({name}, {score}) pasted into db')
            self.db.commit()

        def getScores(self):
            res = ''
            for row in self.cur.execute("SELECT name, score FROM players ORDER BY score DESC LIMIT 5"):
                res += row[0] + ' ' + str(row[1]) + '\n'
            print(f'Results for select statement:\n{res}')
            return res

    class Player(pygame.sprite.Sprite):
        def __init__(self, game):
            super().__init__()
            self.env = game
            self.surf = pygame.Surface((50, 50))
            self.surf.fill((128,255,40))
            self.rect = self.surf.get_rect()
            self.pos = vec((400, 580))
            self.vel = vec(0,0)
            self.acc = vec(0,0)
            self.counter = 0
            self.firerate = 30
            self.name = ''

        def shoot(self):
            coords = list(self.rect.center)
            coords[1] -= 15
            self.env.player_bullets.add(self.env.player_bullet(*coords))
            self.counter = 0

        def move(self):
            self.acc = vec(0,0)
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_LEFT]:
                self.acc.x = -ACC
            if pressed_keys[K_RIGHT]:
                self.acc.x = ACC
            self.acc.x += self.vel.x * FRIC
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc

            if self.pos.x > WIDTH:
                self.pos.x = 0
            if self.pos.x < 0:
                self.pos.x = WIDTH
            self.rect.midbottom = self.pos

        def collide(self): return pygame.sprite.spritecollide(self, self.env.bullets, True)
        def update(self):
            hits = self.collide()
            return hits
        
    class Enemy(pygame.sprite.Sprite):
        def __init__(self, x ,y, game):
            super().__init__()
            self.env = game
            self.surf = pygame.Surface((50, 50))
            self.surf.fill((255,0,0))
            self.rect = self.surf.get_rect(center = (x, y))
            self.counter = 0
            self.firerate = random.uniform(30, 100)
        def shoot(self):
            if (self.counter > self.firerate):
                coords = list(self.rect.center)
                coords[1] += 25
                self.env.bullets.add(self.env.bullet(*coords))
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

    class bullet(pygame.sprite.Sprite):
        def __init__(self, x ,y):
            super().__init__()
            self.surf = pygame.Surface((12, 20))
            self.surf.fill((255,0,0))
            self.rect = self.surf.get_rect(center = (x, y))
        def move(self):
            coords = list(self.rect.center)
            if (coords[1] > HEIGHT): 
                self.kill()
                return
            coords[1] += 10
            self.rect = self.surf.get_rect(center = (coords[0], coords[1]))

    class player_bullet(pygame.sprite.Sprite):
        def __init__(self, x ,y):
            super().__init__()
            self.surf = pygame.Surface((20, 20))
            self.surf.fill((128,255,40))
            self.rect = self.surf.get_rect(center = (x, y))
        def move(self):
            coords = list(self.rect.center)
            if (coords[1] > HEIGHT): 
                self.kill()
                return
            coords[1] -= 10
            self.rect = self.surf.get_rect(center = (coords[0], coords[1]))

    def gameLoop(self):
        scoresflag = True
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if self.PAUSE:
                    self.input_box.handle_event(event)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.P1.name = self.input_box.text
                            self.PAUSE = False
                elif self.WIN or self.LOSE:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            tempname = self.P1.name
                            self.__init__()
                            self.input_box = InputBox.InputBox(20, 80, 300, 60, tempname)
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP and (self.P1.counter > self.P1.firerate):
                            self.P1.shoot()
                            self.P1.counter +=1
            self.display_surface.fill((0,0,0))
        
            if self.PAUSE:
                self.display_surface.blit(self.pause_text_surface, (20, 20))
                self.input_box.update()
                self.input_box.draw(self.display_surface)
                blitMultiline(self.display_surface, 
                        'Use ARROW LEFT & RIGHT to move\n'\
                        'Use ARROW UP to shoot\n'\
                        'You gain more points if you\n'\
                        'shoot enemies earlier\n'\
                        'But after first 60 sec you\n'\
                        'won\'t be getting any\n'\
                        'Press ENTER to save the name and play', 
                        (20, 150), font, (255, 255, 255))
            elif not self.enemies:
                self.WIN = True
                if scoresflag: 
                    self.highscores.pasteNew(self.P1.name, self.score)
                    scoresflag = False
                    scores = self.highscores.getScores()
                blitMultiline(
                    self.display_surface, f'You won! {self.score} points gained.'\
                    'Press ENTER to start everything over\n\n'\
                    f'Top 5 players: \n\n{scores}', 
                    (20, 20), font, (255, 255, 255)
                )
            elif self.LOSE:
                blitMultiline(self.display_surface, 'You lost :( !\nPress ENTER to start everything over', (20, 20), font, (255, 255, 255))
            else:
                self.P1.move()
                self.P1.counter += 1
                if self.P1.update():
                    self.LOSE = True
                for entity in self.enemies:
                    entity.shoot()
                    entity.update()
                    self.display_surface.blit(entity.surf, entity.rect)
                for entity in self.bullets:
                    entity.move()
                    self.display_surface.blit(entity.surf, entity.rect)
                for entity in self.player_bullets:
                    entity.move()
                    self.display_surface.blit(entity.surf, entity.rect)
                self.display_surface.blit(self.P1.surf, self.P1.rect)
            pygame.display.update()
            self.counter +=1
            FramePerSec.tick(FPS)