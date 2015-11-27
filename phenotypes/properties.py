from . import Phenotype


class Properties(Phenotype):
    def __init__(self, *args, **kwargs):
        super(Properties, self).__init__(*args, **kwargs)
        for gene in self.genes:
            i = 0
            while i < len(gene):
                if "".join(gene[i:self.id_length]) in self.list:
                    i += self.decode_property(gene[i:])
                i += self.id_length
        for id_, name in self.list.items():
            if not hasattr(self, name):
                setattr(self, name, self.defaults[name])

    def decode_property(self, gene):
        id_ = "".join(gene[0:self.id_length])
        if hasattr(self, "decode_{0}".format(self.list[id_])):
            return getattr(self, "decode_{0}".format(self.list[id_]))(gene[self.id_length:]) + self.id_length
        else:
            return self.id_length

    def decode_speed(self, gene):
        max_speed = 5
        speed_length = 2
        if len(gene) >= speed_length:
            self.speed = (int("".join(gene[:speed_length]), self.genotype.GENE_BASE) % max_speed) + 1
            return speed_length
        return 0
