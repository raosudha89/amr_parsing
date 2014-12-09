__author__ = 'yogarshi'

import sys
import networkx as nx
import cPickle as pickle

def create_dataset(amr_nx_graphs, concept_data, dep_parse):

    dataset = {}

    count = 0

    for id, value in amr_nx_graphs.iteritems():


        curr_dp = dep_parse[count]

        count += 1

        [root, amr_nx_graph, sentence, alignments] = value
        nodes = amr_nx_graph.nodes(data=True)
        edges = amr_nx_graph.edges(data=True)
        nodes_dict = {x[0]: x[1] for x in nodes}



        concepts = concept_data[id]
        print concepts
        concept_nodes = [x[-1].split('_') for x in concepts]
        concept_dict = {}

        i = 0
        for each_node in concept_nodes:
            for every_element in each_node:
                concept_dict[every_element] = i
            i += 1

        #print concept_nodes
        pos_seq = [x[1] for x in concepts]

        edges_dict = [(nodes_dict[x[0]]['instance'], nodes_dict[x[1]]['instance'], x[2]['relation'],
                       nodes_dict[nodes_dict[x[0]]['parent']]['instance'] if nodes_dict[x[0]]['parent'] is not None else None
                       , nodes_dict[nodes_dict[x[1]]['parent']]['instance'] if nodes_dict[x[1]]['parent'] is not None else None)
                      for x in edges]
        edges_dict_safe = [(x[0], x[1], x[-2], x[-1]) for x in edges_dict]

        temp1 = []
        temp2 = []

        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    node1 = nodes[i][1]['instance']
                    node2 = nodes[j][1]['instance']

                    node1p_t = nodes[i][1]['parent']
                    node2p_t = nodes[j][1]['parent']

                    node1p = nodes_dict[node1p_t]['instance'] if node1p_t is not None else None
                    node2p = nodes_dict[node2p_t]['instance'] if node2p_t is not None else None

                    idx1 = -1
                    idx2 = -1
                    pos1 = "X"
                    pos2 = "X"

                    word1 = "NA"
                    word2 = "NA"
                    dep_rel = "-"

                    if node1 in concept_dict:
                        idx1 = concept_dict[node1]
                        pos1 = pos_seq[idx1]
                        word1 = concepts[idx1][0]
                    if node2 in concept_dict:
                        idx2 = concept_dict[node2]
                        pos2 = pos_seq[idx2]
                        word2 = concepts[idx2][0]

                    word_t = (word1, word2)
                    if word_t in curr_dp:
                        dep_rel = curr_dp[word_t]

                    #Append stuff to the training data list
                    t = (node1, node2, node1p, node2p)
                    if t in edges_dict_safe:
                        idx = edges_dict_safe.index(t)
                        temp1.append((edges_dict[idx], pos1, pos2, idx1, idx2, dep_rel))


        training_data = temp1+temp2
        dataset[id] = training_data

        #print training_data
        #print

    #print count
    return dataset


def main(argv):

    if len(argv) < 2:
        raise Exception("Incorrect number of arguments. Usage : python create_relation_learning_dataset.py "
                        "<amr_nx_graphs.p> <concept_dataset.p> <dep_parse.p>")

    amr_nx_graphs_p = argv[0] #"data/amr-release-1.0-training-bolt/amr_nx_graphs.p"
    concept_training_dataset_p = argv[1] #"data/amr-release-1.0-training-bolt/concept_training_dataset.p"
    dep_parse_p = argv[2] #"dep_parse_training.p"


    #Load the amr_nx_graphs
    amr_nx_graphs = pickle.load(open(amr_nx_graphs_p, "rb"))

    #Load the concept training data set
    concept_training_dataset = pickle.load(open(concept_training_dataset_p, "rb"))

    #Load the dependency parse
    dep_parse = pickle.load(open(dep_parse_p, "rb"))

    #Create the relation training dataset
    dataset = create_dataset(amr_nx_graphs, concept_training_dataset, dep_parse)

    pickle.dump(dataset, open("relation_test_dataset.p", "wb"))


if __name__ == "__main__":
    main(sys.argv[1:])
