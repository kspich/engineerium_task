import pygame
from pygame.locals import *
import sys
import InputBox

from Player import Player
from Enemy import Enemy
from Highscores import Highscores

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
        self.enemies.add(Enemy(WIDTH/2, 50, self))
        dumb_flag = True
        for x in range(WIDTH//2, WIDTH - 10, WIDTH//11):
            if dumb_flag: 
                dumb_flag = not dumb_flag
                continue
            self.enemies.add(Enemy(x, 50, self))
            self.enemies.add(Enemy(WIDTH//2 - (x - WIDTH//2), 50, self))

        self.P1 = Player(self)
        self.player_bullets = pygame.sprite.Group() 
        self.bullets = pygame.sprite.Group()

        self.input_box = InputBox.InputBox(20, 80, 300, 60, 'Player')
        self.highscores = Highscores()

        self.counter = 0
        self.score = 0

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
                    # тот самый топ 5 игроков
                    self.display_surface, 
                    f'You won! {self.score} points gained.\n'\
                    'Press ENTER to start everything over\n\n'\
                    f'Top 5 players: \n\n{scores}', 
                    (20, 20), font, (255, 255, 255)
                )
            elif self.LOSE:
                if scoresflag: 
                    scoresflag = False
                    scores = self.highscores.getScores()
                blitMultiline(
                    self.display_surface,
                    f'You lost :( ! {self.score} points gained.\n'\
                    'Press ENTER to start everything over\n\n'\
                    f'Top 5 players: \n\n{scores}',
                    (20, 20), font, (255, 255, 255)
                )
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