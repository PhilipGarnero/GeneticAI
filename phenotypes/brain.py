import math
import pydot
from time import time

from . import Phenotype


class Brain(Phenotype):
    NEURON_ID_CODE_LENGTH = 1
    CONNECTION_WEIGHT_CODE_LENGTH = 4
    CONNECTION_CODE_LENGTH = 2 * NEURON_ID_CODE_LENGTH + CONNECTION_WEIGHT_CODE_LENGTH

    def __init__(self, *args, **kwargs):
        super(Brain, self).__init__(*args, **kwargs)
        self.inputs = []
        self.hiddens = []
        self.outputs = []
        self.connections = []
        self.gene_parser()

    def gene_parser(self):
        base_10_max = float(self.genotype.GENE_BASE**self.CONNECTION_WEIGHT_CODE_LENGTH / 2)
        connections = []
        for gene in self.genes:
            codes = ["".join(gene[i:i + self.CONNECTION_CODE_LENGTH])
                     for i in xrange(0, len(gene), self.CONNECTION_CODE_LENGTH)]
            if len(codes[-1]) < self.CONNECTION_CODE_LENGTH:
                del codes[-1]
            for code in codes:
                in_neuron_id = int(code[:self.NEURON_ID_CODE_LENGTH], self.genotype.GENE_BASE)
                weight = (float(int(code[self.NEURON_ID_CODE_LENGTH:self.NEURON_ID_CODE_LENGTH + self.CONNECTION_WEIGHT_CODE_LENGTH], self.genotype.GENE_BASE)) - base_10_max) / base_10_max
                out_neuron_id = int(code[self.NEURON_ID_CODE_LENGTH + self.CONNECTION_WEIGHT_CODE_LENGTH:], self.genotype.GENE_BASE)
                connections.append((in_neuron_id, weight, out_neuron_id))
        self.net_builder(connections)

    def net_builder(self, connections):
        ins = []
        outs = []
        tree = {}

        def path_checker(path, check):
            if check in path:
                raise RuntimeError
            else:
                path.append(check)
                if check in tree:
                    for con in [x["to"] for x in tree[check]]:
                        path_checker(list(path), con)

        for connection in connections:
            try:
                path_checker([connection[0]], connection[2])
            except RuntimeError:
                continue
            if connection[0] not in tree:
                tree[connection[0]] = []
            tree[connection[0]].append({"to": connection[2], "weight": connection[1]})
            ins.append(connection[0])
            outs.append(connection[2])
        inputs = list(set(ins) - set(outs))
        outputs = list(set(outs) - set(ins))

        def tree_builder(neuron_id):
            neuron = self.get_neuron(neuron_id)
            if neuron is None:
                if neuron_id in inputs:
                    neuron = InputNeuron(neuron_id)
                    self.inputs.append(neuron)
                elif neuron_id in outputs:
                    neuron = OutputNeuron(neuron_id)
                    self.outputs.append(neuron)
                else:
                    neuron = Neuron(neuron_id)
                    self.hiddens.append(neuron)
            if neuron_id in tree:
                for connection in tree.pop(neuron_id):
                    synapse = Synapse(connection["weight"], neuron, tree_builder(connection["to"]))
                    self.connections.append(synapse)
                    neuron.add_connection(synapse)
            return neuron

        for neuron_id in inputs:
            tree_builder(neuron_id)

    def get_neuron(self, neuron_id):
        try:
            index = self.hiddens.index(neuron_id)
            return self.hiddens[index]
        except ValueError:
            try:
                index = self.inputs.index(neuron_id)
                return self.inputs[index]
            except ValueError:
                try:
                    index = self.outputs.index(neuron_id)
                    return self.outputs[index]
                except ValueError:
                    return None

    def think(self, inputs, output_dimension):
        for value, neuron in zip(inputs, self.inputs):
            neuron.activate(value)
        results = []
        for neuron in self.outputs:
            results.append(neuron.value)
            neuron.reset()
        for neuron in self.inputs:
            neuron.reset()
        for neuron in self.hiddens:
            neuron.reset()
        for connection in self.connections:
            connection.alter_weight()
            connection.reset
        output_filler = [0.0 for _ in range(output_dimension)]
        output_filler[:len(results)] = results[:output_dimension]
        return output_filler

    def draw_net(self, filename):
        graph = pydot.Dot(graph_type='digraph')
        graph.set_rankdir('LR')
        drawn = []

        def add_edges(neurons, level=0):
            for neuron in neurons:
                for synapse in neuron.connections:
                    if synapse in drawn:
                        continue
                    else:
                        drawn.append(synapse)
                    if level == 0:
                        start_node = pydot.Node(neuron.id, style="filled", fillcolor="#77DD77")
                    else:
                        start_node = pydot.Node(neuron.id, style="filled", fillcolor="#AEC6CF")
                    if len(synapse.aim.connections) > 0:
                        end_node = pydot.Node(synapse.aim.id, style="filled", fillcolor="#AEC6CF")
                    else:
                        end_node = pydot.Node(synapse.aim.id, style="filled", fillcolor="#FF6961")
                    graph.add_node(start_node)
                    graph.add_node(end_node)
                    graph.add_edge(pydot.Edge(start_node, end_node, label=str(synapse.weight)))
                aims = [c.aim for c in neuron.connections]
                add_edges(aims, level + 1)

        add_edges(self.inputs)
        graph.write_png(filename)


class Neuron(object):
    TRESHOLD_LEVEL = 0.5
    DECAY_RATE = 4

    def __init__(self, id_, connections=None):
        self.id = id_
        self.connections = connections or []
        self.value = 0.0
        self.has_fired = False
        self.last_activation = time()

    def __eq__(self, other):
        if isinstance(other, Neuron):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        else:
            return False

    def add_connection(self, connection):
        self.connections.append(connection)

    def activate(self, value):
        activation_time = time()
        self.value *= self.exp_decay((activation_time - self.last_activation) * 1000)
        self.last_activation = activation_time
        self.value += value
        if self.value > self.TRESHOLD_LEVEL:
            self.fire()

    def fire(self):
        if not self.has_fired:
            for connection in self.connections:
                connection.propagate()
            self.has_fired = True

    def reset(self):
        self.has_fired = False

    @classmethod
    def exp_decay(cls, x):
        return math.exp(-float(x) * float(cls.DECAY_RATE))


class InputNeuron(Neuron):
    def activate(self, value):
        self.value = value
        self.fire()

    def fire(self):
        for connection in self.connections:
            connection.propagate(self.value)


class OutputNeuron(Neuron):
    def reset(self):
        self.value = 0.0

    def activate(self, value):
        self.value += value


class Synapse(object):
    WEIGHT_ALTERATION_FACTOR = 0.0005

    def __init__(self, weight, origin, aim):
        self.weight = weight
        self.origin = origin
        self.aim = aim
        self.used = False

    def propagate(self, value=None):
        if value is not None:
            # That means the origin is an input neuron
            self.aim.activate(value * self.weight)
        else:
            self.aim.activate(self.weight)
        self.used = self.aim.has_fired
        if self.weight < 0.0:
            self.used = not self.used

    def alter_weight(self):
        if self.used:
            self.weight += self.weight * self.WEIGHT_ALTERATION_FACTOR
        else:
            self.weight -= self.weight * self.WEIGHT_ALTERATION_FACTOR

    def reset(self):
        self.used = False
