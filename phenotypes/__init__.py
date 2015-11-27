class Phenotype(object):
    def __init__(self, genotype, genes, definition):
        self.genotype = genotype
        self.genes = genes
        self.definition = definition

    def __getattr__(self, attr):
        try:
            return self.definition[attr]
        except KeyError:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__, attr))

    @property
    def viable(self):
        return True
