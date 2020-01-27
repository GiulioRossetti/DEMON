import networkx as nx
import random
import time
import sys
import tqdm
import os

__author__ = "Giulio Rossetti"
__contact__ = "giulio.rossetti@isti.cnr.it"
__license__ = "BSD 2 Clause"


def timeit(method):
    """
    Decorator: Compute the execution time of a function
    :param method: the function
    :return: the method runtime
    """

    def timed(*arguments, **kw):
        ts = time.time()
        result = method(*arguments, **kw)
        te = time.time()

        sys.stdout.write('Time:  %r %2.2f sec\n' % (method.__name__.strip("_"), te - ts))
        sys.stdout.write('------------------------------------\n')
        sys.stdout.flush()
        return result

    return timed


class Demon(object):
    """
    Flat Merge version of Demon algorithm as described in:

    Michele Coscia, Giulio Rossetti, Fosca Giannotti, Dino Pedreschi:
    DEMON: a local-first discovery method for overlapping communities.
    KDD 2012:615-623
    """

    def __init__(self, graph=None, network_filename=None, epsilon=0.25, min_community_size=3, file_output=None):
        """
        Constructor

        :@param network_filename: the networkx filename
        :@param epsilon: the tolerance required in order to merge communities
        :@param min_community_size:min nodes needed to form a community
        :@param file_output: True/False
        """
        if graph is None:
            self.g = nx.Graph()
            if network_filename is not None:
                self.__read_graph(network_filename)
            else:
                raise ImportError
        else:
            self.g = graph
        self.epsilon = epsilon
        self.min_community_size = min_community_size
        self.file_output = file_output
        self.base = os.getcwd()

    @timeit
    def __read_graph(self, network_filename):
        """
        Read .ncol network file

        :param network_filename: complete path for the .ncol file
        :return: an undirected network
        """
        self.g = nx.read_edgelist(network_filename, nodetype=int)

    @timeit
    def execute(self):
        """
        Execute Demon algorithm

        """

        for n in self.g.nodes():
            self.g.nodes[n]['communities'] = [n]

        all_communities = {}

        for ego in tqdm.tqdm(nx.nodes(self.g), ncols=35, bar_format='Exec: {l_bar}{bar}'):

            ego_minus_ego = nx.ego_graph(self.g, ego, 1, False)
            community_to_nodes = self.__overlapping_label_propagation(ego_minus_ego, ego)

            # merging phase
            for c in community_to_nodes.keys():
                if len(community_to_nodes[c]) > self.min_community_size:
                    actual_community = community_to_nodes[c]
                    all_communities = self.__merge_communities(all_communities, actual_community)

        # write output on file
        if self.file_output:
            with open(self.file_output, "w") as out_file_com:
                for idc, c in enumerate(all_communities.keys()):
                    out_file_com.write("%d\t%s\n" % (idc, str(sorted(c))))

        return list(all_communities.keys())

    @staticmethod
    def __overlapping_label_propagation(ego_minus_ego, ego, max_iteration=10):
        """

        :@param max_iteration: number of desired iteration for the label propagation
        :@param ego_minus_ego: ego network minus its center
        :@param ego: ego network center
        """
        t = 0

        old_node_to_coms = {}

        while t <= max_iteration:
            t += 1

            node_to_coms = {}

            nodes = list(nx.nodes(ego_minus_ego))
            random.shuffle(nodes)

            count = -len(nodes)

            for n in nodes:
                label_freq = {}

                n_neighbors = list(nx.neighbors(ego_minus_ego, n))

                if len(n_neighbors) < 1:
                    continue

                # compute the frequency of the labels
                for nn in n_neighbors:

                    communities_nn = [nn]

                    if nn in old_node_to_coms:
                        communities_nn = old_node_to_coms[nn]

                    for nn_c in communities_nn:
                        if nn_c in label_freq:
                            v = label_freq.get(nn_c)
                            label_freq[nn_c] = v + 1
                        else:
                            label_freq[nn_c] = 1

                # first run, random community label initialization
                if t == 1:
                    if not len(n_neighbors) == 0:
                        r_label = random.sample(label_freq.keys(), 1)
                        ego_minus_ego.nodes[n]['communities'] = r_label
                        old_node_to_coms[n] = r_label
                    count += 1
                    continue

                # choosing the majority
                else:
                    labels = []
                    max_freq = -1

                    for l, c in label_freq.items():
                        if c > max_freq:
                            max_freq = c
                            labels = [l]
                        elif c == max_freq:
                            labels.append(l)

                    node_to_coms[n] = labels

                    if n not in old_node_to_coms or not set(node_to_coms[n]) == set(old_node_to_coms[n]):
                        old_node_to_coms[n] = node_to_coms[n]
                        ego_minus_ego.nodes[n]['communities'] = labels

        # build the communities reintroducing the ego
        community_to_nodes = {}
        for n in nx.nodes(ego_minus_ego):
            if len(list(nx.neighbors(ego_minus_ego, n))) == 0:
                ego_minus_ego.nodes[n]['communities'] = [n]

            c_n = ego_minus_ego.nodes[n]['communities']

            for c in c_n:

                if c in community_to_nodes:
                    com = community_to_nodes.get(c)
                    com.append(n)
                else:
                    nodes = [n, ego]
                    community_to_nodes[c] = nodes

        return community_to_nodes

    def __merge_communities(self, communities, actual_community):
        """

        :param communities: dictionary of communities
        :param actual_community: a community
        """

        # if the community is already present return
        if tuple(actual_community) in communities:
            return communities

        else:
            # search a community to merge with
            inserted = False

            for test_community in communities.items():

                union = self.__generalized_inclusion(actual_community, test_community[0])

                # community to merge with identified!
                # N.B. one-to-one merge with no predefined visit ordering: non-deterministic behaviours expected
                if union is not None:
                    communities.pop(test_community[0])
                    communities[tuple(sorted(union))] = 0
                    inserted = True
                    break

            # not merged: insert the original community
            if not inserted:
                communities[tuple(sorted(actual_community))] = 0

        return communities

    def __generalized_inclusion(self, c1, c2):
        """

        :param c1: community
        :param c2: community
        """
        intersection = set(c2) & set(c1)
        smaller_set = min(len(c1), len(c2))

        if len(intersection) == 0:
            return None

        res = 0
        if not smaller_set == 0:
            res = float(len(intersection)) / float(smaller_set)

        if res >= self.epsilon:  # at least e% of similarity wrt the smallest set
            union = set(c2) | set(c1)
            return union
        return None


def main():
    import argparse

    sys.stdout.write("-------------------------------------\n")
    sys.stdout.write("              {DEMON}                \n")
    sys.stdout.write("     Democratic Estimate of the      \n")
    sys.stdout.write("  Modular Organization of a Network  \n")
    sys.stdout.write("-------------------------------------\n")
    sys.stdout.write("Author: " + __author__ + "\n")
    sys.stdout.write("Email:  " + __contact__ + "\n")
    sys.stdout.write("------------------------------------\n")

    parser = argparse.ArgumentParser()

    parser.add_argument('network_file', type=str, help='network file (edge list format)')
    parser.add_argument('epsilon', type=float, help='merging threshold')
    parser.add_argument('-c', '--min_com_size', type=int, help='minimum community size', default=3)

    args = parser.parse_args()
    dm = Demon(g=None, network_filename=args.network_file, epsilon=args.epsilon,
               min_community_size=args.min_com_size, file_output="demon_communities.tsv")
    dm.execute()

