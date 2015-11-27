from . import Phenotype


class Body(Phenotype):
    def __init__(self, *args, **kwargs):
        super(Body, self).__init__(*args, **kwargs)
        self.color = None
        self.polygon = None
        for gene in self.genes:
            if len(gene) > self.color_length:
                self.color = int("".join(gene[:self.color_length]), self.genotype.GENE_BASE)
            self.polygon = [(int("".join(gene[i:i+self.apex_length/2]), self.genotype.GENE_BASE),
                             int("".join(gene[i+self.apex_length/2:i+self.apex_length]), self.genotype.GENE_BASE))
                            for i in xrange(self.color_length, len(gene) - self.apex_length, self.apex_length)]
            if len(self.polygon) < 3:
                self.polygon = None

    def parts(self):
        return [(self.color, self.polygon)]
