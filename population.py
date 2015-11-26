import random


class Population(object):
    def __init__(self, rank_probability=0.2, reverse_sort=False):
        self.actors = []
        self.sorted = False
        self.rank_probability = rank_probability
        self.reverse_sort = reverse_sort

    def __len__(self):
        return len(self.actors)

    def __getitem__(self, key):
        return self.actors[key]

    def __iter__(self):
        return iter(self.actors)

    def __setitem__(self, key, value):
        self.actors[key] = value
        self.sorted = False

    def __repr__(self):
        s = "---------------------------------\n"
        for actor in self.actors:
            s += str(actor)
            s += "\n"
        s += "---------------------------------"
        return s

    def append(self, elem):
        self.actors.append(elem)
        self.sorted = False

    def select_best_fitness(self):
        self.sort()
        return self.actors[0]

    def select_worst_fitness(self):
        self.sort()
        return self.actors[-1]

    def select_by_rank(self):
        self.sort()
        for actor in self.actors:
            if random.random() < self.rank_probability:
                return actor
        return self.actors[-1]

    @staticmethod
    def cmp_actors(a, b):
        if a.fitness < b.fitness:
            return -1
        if a.fitness > b.fitness:
            return 1
        return 0

    def sort(self):
        """evaluate should always be called before sorting"""
        if self.sorted:
            return
        self.actors.sort(cmp=self.cmp_actors, reverse=self.reverse_sort)
        self.sorted = True

    def clear(self):
        self.actors = []
        self.sorted = False

    def evaluate(self, *args, **kwargs):
        for actor in self.actors:
            actor.fitness_evaluation(*args, **kwargs)
        self.sorted = False
