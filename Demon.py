import networkx as nx
import random
import time
import sys
import matplotlib.pyplot as plt

__author__ = "Giulio Rossetti"
__contact__ = "giulio.rossetti@isti.cnr.it"
__license__ = "BSD"


def timeit(method):

    def timed(*argst, **kwt):
        ts = time.time()
        result = method(*argst, **kwt)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, argst, kwt, te-ts)
        return result

    return timed


class Demon(object):
    """
    Flat Merge version of Demon algorithm as described in:

    Michele Coscia, Giulio Rossetti, Fosca Giannotti, Dino Pedreschi:
    DEMON: a local-first discovery method for overlapping communities.
    KDD 2012:615-623
    """

    def __init__(self, network_filename, epsilon=0.25, min_community_size=3, file_output=True, output_filename='output'):
        """
        Constructor

        :@param network_filename: the networkx filename
        :@param epsilon: the tolerance required in order to merge communities
        :@param min_community_size:min nodes needed to form a community
        :@param file_output: True/False
        """

        self.g = nx.Graph()
        self.__read_graph(network_filename)
        self.epsilon = epsilon
        self.min_community_size = min_community_size
        self.file_output = file_output
        self.output_filename = output_filename

    @timeit
    def __read_graph(self, network_filename):

        sys.stdout.write('[Graph Loading]\n')
        sys.stdout.flush()
        old_p = 0
        actual = 1
        bar_length = 20
        num_lines = sum([1 for i in open(network_filename)])

        f = open(network_filename)

        for l in f:
            try:
                l = map(int, l.rstrip().replace("\t", ";").replace(" ", ";").split(";")[:2])
                self.g.add_edge(l[0], l[1])
            except ValueError:
                pass

            percentage = int((float(actual) / num_lines) * 100)
            if percentage > old_p:
                hashes = '#' * int(round(percentage/5))
                spaces = ' ' * (bar_length - len(hashes))
                sys.stdout.write("\rExec: [{0}] {1}%".format(hashes + spaces, int(round(percentage))))
                sys.stdout.flush()
                old_p = percentage

            actual += 1

        sys.stdout.write("\nStat: Nodes %d Edges %d" % (self.g.number_of_nodes(), self.g.number_of_edges()))
        sys.stdout.flush()

    @timeit
    def execute(self):
        """
        Execute Demon algorithm

        """

        sys.stdout.write('\n[Community Extraction]\n')
        sys.stdout.flush()

        for n in self.g.nodes():
            self.g.node[n]['communities'] = [n]

        all_communities = {}

        total_nodes = len(nx.nodes(self.g))
        old_p = 0
        actual = 1

        bar_length = 20

        for ego in nx.nodes(self.g):

            ego_minus_ego = nx.ego_graph(self.g, ego, 1, False)
            community_to_nodes = self.__overlapping_label_propagation(ego_minus_ego, ego)

            # merging phase
            for c in community_to_nodes.keys():
                if len(community_to_nodes[c]) > self.min_community_size:
                    actual_community = community_to_nodes[c]
                    all_communities = self.__merge_communities(all_communities, actual_community)

            # progress bar update
            percentage = int(float(actual * 100) / total_nodes)
            if percentage > old_p:
                hashes = '#' * int(round(percentage/5))
                spaces = ' ' * (bar_length - len(hashes))
                sys.stdout.write("\rExec: [{0}] {1}%".format(hashes + spaces, int(round(percentage))))
                sys.stdout.flush()
                old_p = percentage
            actual += 1

        if self.file_output:
            out_file_com = open("%s.txt" % self.output_filename, "w")
            idc = 0
            for c in all_communities.keys():
                out_file_com.write("%d\t%s\n" % (idc, str(sorted(c))))
                idc += 1
            out_file_com.flush()
            out_file_com.close()
        else:
            return all_communities
        self.plot(all_communities)

    @staticmethod
    def __overlapping_label_propagation(ego_minus_ego, ego, max_iteration=10):
        """

        :@param max_iteration: number of desired iteration for the label propagation
        :@param ego_minus_ego: ego network minus its center
        :@param ego: ego network center
        """
        t = 0

        old_node_to_coms = {}

        while t < max_iteration:
            t += 1

            node_to_coms = {}

            nodes = nx.nodes(ego_minus_ego)
            random.shuffle(nodes)

            count = -len(nodes)

            for n in nodes:
                label_freq = {}

                n_neighbors = nx.neighbors(ego_minus_ego, n)

                if len(n_neighbors) < 1:
                    continue

                if count == 0:
                    t += 1

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

                # first run, random choosing of the communities among the neighbors labels
                if t == 1:
                    if not len(n_neighbors) == 0:
                        r_label = random.sample(label_freq.keys(), 1)
                        ego_minus_ego.node[n]['communities'] = r_label
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
                        ego_minus_ego.node[n]['communities'] = labels

            t += 1

        # build the communities reintroducing the ego
        community_to_nodes = {}
        for n in nx.nodes(ego_minus_ego):
            if len(nx.neighbors(ego_minus_ego, n)) == 0:
                ego_minus_ego.node[n]['communities'] = [n]

            c_n = ego_minus_ego.node[n]['communities']

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
            # print len(communities)

            for test_community in communities.items():

                union = self.__generalized_inclusion(actual_community, test_community[0])

                # community to merge with found!
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

    def plot(self, all_communities):
        try:
            pos = nx.nx_agraph.graphviz_layout(self.g)
        except:
            pos = nx.spring_layout(self.g, iterations=20)
        node_color = 'grey'
        colors = ['yellow', 'blue', 'green', 'red', 'orange', 'brown', 'black']
        count = 0
        plt.rcParams['text.usetex'] = False
        plt.figure(figsize=(20, 20))
        plt.axis('off')
        for list_nodes in all_communities.keys():
            if count < len(colors):
                node_color = colors[count]
            print node_color
            nx.draw_networkx_nodes(self.g, pos, list_nodes, alpha=0.5, node_size=20,
                                   node_color=node_color)
            if len(list_nodes) > 1:
                list_edges = [(u, v) for (u, v) in self.g.edges()
                              if u in list_nodes and v in list_nodes]

                nx.draw_networkx_edges(self.g, pos, list_edges, alpha=0.5, node_size=0, width=0.1, edge_color=node_color)
            count += 1

        plt.savefig('{}_{}.png'.format(self.output_filename, count), dpi=75, transparent=False)
        plt.close()

# if __name__ == "__main__":
#     import argparse
#
#     print "-------------------------------------"
#     print "              {DEMON}                "
#     print "     Democratic Estimate of the      "
#     print "  Modular Organization of a Network  "
#     print "-------------------------------------"
#     print "Author: ", __author__
#     print "Email:  ", __contact__
#     print "------------------------------------\n"
#
#     parser = argparse.ArgumentParser()
#
#     parser.add_argument('network_file', type=str, help='network file (edge list format)')
#     parser.add_argument('epsilon', type=float, help='merging threshold')
#     parser.add_argument('-c', '--min_com_size', type=int, help='minimum community size', default=3)
#     parser.add_argument('-o', '--out_file', type=str, help='output file', default="demon_coms.txt")
#
#     args = parser.parse_args()
#     dm = Demon(args.network_file, epsilon=args.epsilon,
#                min_community_size=args.min_com_size, file_output=args.out_file)
#     dm.execute()




