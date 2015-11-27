import random
from collections import deque
from phenotypes.brain import Brain
from phenotypes.body import Body
from phenotypes.properties import Properties


class Genotype(object):
    GENE_MUTATION_PROB = 0.50
    GENE_IF_MUTATION_ADD_PROB = 0.10
    GENE_IF_MUTATION_NO_ADD_DEL_PROB = 0.10
    GENE_CROSSOVER_PROB = 0.70
    GENE_IF_CROSSOVER_DOUBLE_PROB = 0.40
    GENE_IF_CROSSOVER_AND_DOUBLE_UNBALANCED_PROB = 0.10
    GENE_CHAR_POOL = "0123456789ABCDEF"
    GENE_BASE = len(GENE_CHAR_POOL)
    GENE_LENGTH = [100, 200]
    GENE_IMPORTANT_CODE_NUMBER = [5, 10]
    GENE_STEP = 2
    GENE_START = "00"
    GENE_STOP = "FF"
    GENE_DEFINITION = {
        "body": {
            "gene_id": "01",
            "required": False,
            "phenotype": Body,
            "apex_length": 2,
            "color_length": 3,
        },
        "brain": {
            "gene_id": "02",
            "required": True,
            "phenotype": Brain,
            "neuron_id_code_length": 1,
            "connection_weight_code_length": 4,
        },
        "properties": {
            "gene_id": "03",
            "required": False,
            "phenotype": Properties,
            "id_length": 1,
            "list": {
                "1": "speed"
            },
            "defaults": {
                "speed": 1
            },
        }
    }

    def __init__(self, dna=None):
        self._genes = None
        self.dna = dna
        if self.dna is None:
            self.generate_dna()

    def __str__(self):
        return "".join(self.dna)

    def generate_dna(self):
        important_codes = [self.GENE_START, self.GENE_STOP]
        gene_codes = [x["gene_id"] for x in self.GENE_DEFINITION.values()]
        self.dna = []
        while not self.viable:
            self.dna = [random.choice(self.GENE_CHAR_POOL) for _ in
                        xrange(random.randint(self.GENE_LENGTH[0], self.GENE_LENGTH[1]))]
            for _ in xrange(random.randint(self.GENE_IMPORTANT_CODE_NUMBER[0],
                                           self.GENE_IMPORTANT_CODE_NUMBER[1])):
                where = random.randint(self.GENE_STEP, len(self.dna) - 2 * self.GENE_STEP)
                where -= where % self.GENE_STEP
                code = random.choice(important_codes)
                self.dna[where:where + self.GENE_STEP] = list(code)
                if code == self.GENE_START:
                    self.dna[where + self.GENE_STEP:where + self.GENE_STEP * 2] = list(random.choice(gene_codes))
            self.extract_genes()

    def extract_genes(self):
        genes = {}
        dna_seq = deque(self.dna[i:i + self.GENE_STEP]
                        for i in xrange(0, len(self.dna), self.GENE_STEP))
        gene = []
        in_gene_sequence = False
        while dna_seq:
            code = "".join(dna_seq.popleft())
            if code == self.GENE_START and not in_gene_sequence:
                in_gene_sequence = True
                gene_id = True
                gene = []
            elif code == self.GENE_STOP and in_gene_sequence:
                # Prevent insertion of empty genes
                if gene_id is not True and gene:
                    genes[gene_id].append(gene)
                in_gene_sequence = False
            elif in_gene_sequence and gene_id is True:
                    gene_id = code
                    if gene_id not in genes:
                        genes[gene_id] = []
            elif in_gene_sequence:
                gene.extend(list(code))
        self._genes = genes

    def get_genes(self):
        if self._genes is None:
            self.extract_genes()
        return self._genes

    def set_genes(self, genes):
        self._genes = genes

    genes = property(get_genes, set_genes)

    def get_genes_for_phenotype(self, name):
        return self.genes.get(self.GENE_DEFINITION[name]['gene_id'], [])

    def get_phenotype(self, name):
        return self.GENE_DEFINITION[name]["phenotype"](self, self.get_genes_for_phenotype(name), self.GENE_DEFINITION[name])

    @property
    def viable(self):
        for name in self.GENE_DEFINITION.keys():
            if self.GENE_DEFINITION[name]['required'] and not self.get_genes_for_phenotype(name):
                return False
        return True

    def mutate(self):
        if random.random() < self.GENE_MUTATION_PROB:
            if random.random() < self.GENE_IF_MUTATION_ADD_PROB:
                self.dna.insert(random.randint(0, len(self.dna) - 1), random.choice(self.GENE_CHAR_POOL))
            elif random.random() < self.GENE_IF_MUTATION_NO_ADD_DEL_PROB:
                del self.dna[random.randint(0, len(self.dna) - 1)]
            else:
                self.dna[random.randint(0, len(self.dna) - 1)] = random.choice(self.GENE_CHAR_POOL)

    @classmethod
    def crossover(cls, father_dna, mother_dna):
        max_cut = len(min(father_dna, mother_dna)) - 1
        if random.random() < cls.GENE_CROSSOVER_PROB:
            cut1 = random.randint(0, max_cut)
            if random.random() < cls.GENE_IF_CROSSOVER_DOUBLE_PROB:
                cut2 = random.randint(0, max_cut)
                if cut2 < cut1:
                    cut1, cut2 = cut2, cut1
                if random.random() < cls.GENE_IF_CROSSOVER_AND_DOUBLE_UNBALANCED_PROB:
                    cut3 = random.randint(0, max_cut)
                    if cut3 < cut1:
                        cut1, cut3 = cut3, cut1
                    child_dna = father_dna[:cut1] + mother_dna[cut1:cut2] + father_dna[cut3:]
                else:
                    child_dna = father_dna[:cut1] + mother_dna[cut1:cut2] + father_dna[cut2:]
            else:
                child_dna = father_dna[:cut1] + mother_dna[cut1:]
        else:
            child_dna = random.choice([father_dna, mother_dna])
        return child_dna

    @classmethod
    def reproduce(cls, father, mother):
        child_dna = cls.crossover(father.dna, mother.dna)
        child = cls(child_dna)
        child.mutate()
        return child
