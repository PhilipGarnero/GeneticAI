import random
from . import Phenotype


class Body(Phenotype):
    APEX_STEP = 2

    def __init__(self, *args, **kwargs):
        super(Body, self).__init__(*args, **kwargs)
        self.polygons = []
        self.polygons.append([(0, 0), (5, 0), (5, 5), (0, 5)])
        self.colors = [random.randint(0x000000, 0xFFFFFF)]
        # for gene in genes:
        #     shape = [int(gene[i:i+2], 16) for i in xrange(0, len(gene - 2), self.APEX_STEP)]
        #     self.polygons.append(shape)

    def parts(self):
        return zip(self.colors, self.polygons)
