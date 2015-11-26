import math
import random
from genotype import Genotype


class Actor(object):
    def __init__(self, world, id_, fitness_evaluation, genotype=None, position=None):
        self.world = world
        self.id = id_
        self._fitness_evaluation_function = fitness_evaluation
        self._fitness = None
        self.genotype = genotype or Genotype()
        self.brain = self.genotype.get_phenotype("brain")
        self.properties = self.genotype.get_phenotype("properties")
        self.body = self.genotype.get_phenotype("body")
        positions = [(0, 0), (world.SIZE[0], 0), (0, world.SIZE[1]), (world.SIZE[0], world.SIZE[1])]
        self.position = position or random.choice(positions)# (random.randint(0, world.SIZE[0]),
                                    # random.randint(0, world.SIZE[1]))

    def __repr__(self):
        return "{1}  {0}  {2}".format(self._fitness, self.id, self.genotype)

    def fitness_evaluation(self, *args, **kwargs):
        self._fitness = self._fitness_evaluation_function(self, *args, **kwargs)
        return self._fitness

    def get_fitness(self):
        if self._fitness is None:
            self.fitness_evaluation()
        return self._fitness

    def set_fitness(self, fitness):
        self._fitness = fitness

    fitness = property(get_fitness, set_fitness)

    def directions_to_center(self):
        x = self.world.point[0] - self.position[0]
        y = self.world.point[1] - self.position[1]
        vec_len = float(math.sqrt((abs(x)**2) + (abs(y)**2)))
        norm_x = float(x) / vec_len
        norm_y = float(y) / vec_len
        return norm_x, norm_y

    def update(self):
        xu, yu = self.directions_to_center()
        x, y = self.brain.think([xu, yu], 2)
        self.move(x, y)

        for color, shape in self.body.parts():
            self.world.draw(color, self.translate_shape(shape))

    def move(self, where_x, where_y):
        xo, yo = self.position
        xo += where_x * self.world.tslf / 10
        yo += where_y * self.world.tslf / 10
        self.position = min(max(0, xo), self.world.SIZE[0] - 5), min(max(0, yo), self.world.SIZE[1] - 5)

    def translate_shape(self, shape):
        return map(lambda p: tuple(map(sum, zip(p, self.position))), shape)

    def brain_graph(self):
        self.brain.draw_net("graph{0}.png".format(self.id))
