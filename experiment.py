import math
import random
from genotype import Genotype
from world import World
from actor import Actor
from population import Population


class Experiment(object):
    POP_SIZE = 500
    RANDOM_ACTORS_NUMBER = 50
    RANK_PROBABILITY_CONSTANT = 0.2

    def __init__(self):
        self.world = World(self)
        self.population = Population(rank_probability=self.RANK_PROBABILITY_CONSTANT, reverse_sort=False)
        self.pop_index = 1
        self.current_generation = 1

    def start(self):
        for _ in xrange(self.POP_SIZE):
            self.population.append(self.create_actor())
        self.world.start()

    @staticmethod
    def evaluate_fitness(actor):
        if actor.dead:
            return 0xFFFFFFF
        x = actor.position[0] - float(actor.world.point[0])
        y = actor.position[1] - float(actor.world.point[1])
        vec_len = float(math.sqrt((x**2) + (y**2)))
        color_diff = float(abs(0x00F - actor.body.color))
        vertex_handicap = float(len(actor.body.polygon)**3)
        return vec_len + color_diff + vertex_handicap

    def create_actor(self, genotype=None):
        actor = Actor(self.world, self.pop_index, self.evaluate_fitness, genotype=genotype, position=(0, 0))
        self.pop_index += 1
        return actor

    def next_generation(self):
        self.world.stop()
        self.population.evaluate()
        new_pop = Population(rank_probability=self.RANK_PROBABILITY_CONSTANT, reverse_sort=False)
        for _ in xrange(self.RANDOM_ACTORS_NUMBER):
            new_pop.append(self.create_actor())
        for _ in xrange(self.POP_SIZE - self.RANDOM_ACTORS_NUMBER):
            new_genotype = Genotype.reproduce(self.population.select_by_rank().genotype,
                                              self.population.select_by_rank().genotype)
            new_pop.append(self.create_actor(genotype=new_genotype))
        self.population = new_pop
        self.current_generation += 1
        self.world.start()

    def update(self):
        for actor in self.population:
            actor.update()

    def stop(self):
        self.world.stop()
        self.population.select_best_fitness().brain_graph()
