import time
import random
import pygame
from pygame.locals import *


class World(object):
    FPS = 30
    SIZE = (1024, 768)
    TIME_BETWEEN_GEN = 4

    def __init__(self, experiment):
        self.experiment = experiment
        self.screen = pygame.display.set_mode(self.SIZE, DOUBLEBUF)
        self.time = pygame.time.Clock()
        self.paused = False
        self.loop = True
        self.tslf = 0  # time since last frame in milliseconds

    def interact(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.experiment.stop()
            if event.type == KEYDOWN:
                pass
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.experiment.stop()
                if event.key == K_p:
                    if self.paused:
                        self.resume()
                    else:
                        self.pause()
                if event.key == K_n:
                    self.experiment.next_generation()

    def start(self):
        pygame.display.set_caption('Generation {0}'.format(self.experiment.current_generation))
        self.point = (random.randint(100, self.SIZE[0]-100),
                      random.randint(100, self.SIZE[1]-100))
        next_gen = time.time()
        self.loop = True
        while self.loop:
            self.interact()
            if self.loop and not self.paused:
                self.loop_step()
                if self.TIME_BETWEEN_GEN and time.time() - next_gen > self.TIME_BETWEEN_GEN:
                    self.experiment.next_generation()

    def stop(self):
        self.loop = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        self.time.tick(self.FPS)

    def loop_step(self):
        self.tslf = float(self.time.tick(self.FPS))
        self.screen.fill(0)
        pygame.draw.polygon(self.screen, 0xFFFFFF, map(lambda p: tuple(map(sum, zip(p, self.point))), [(0, 0), (5, 0), (5, 5), (0, 5)]))
        self.experiment.update()
        pygame.display.flip()

    def draw(self, color, points):
        pygame.draw.polygon(self.screen, color, points)
