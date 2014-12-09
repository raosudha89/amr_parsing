import sys
import cPickle as pickle
from collections import OrderedDict

argv = sys.argv[1:]
if len(argv) < 1:
    print "usage: create_nodes_relation_dict.py <relation_training_dataset.p>"
    sys.exit()

relation_training_dataset = pickle.load(open(argv[0], "rb"))

nodes_relation_dict = {}

count = 0
for id, relation_training_data in relation_training_dataset.iteritems():
    count += 1
    for edge in relation_training_data:
        #print edge[0][0]
        #print edge[0][1]
        t = (edge[0][0], edge[0][1])
        relation = edge[0][2]

        if relation == "NULL":
            continue

        """
        if t not in nodes_relation_dict:
            nodes_relation_dict[t] = {}
        if relation not in nodes_relation_dict[t]:
            nodes_relation_dict[t][relation] = 0

        nodes_relation_dict[t][relation] += 1

        """
        if t[0] not in nodes_relation_dict:
            nodes_relation_dict[t[0]] = {}
        if relation not in nodes_relation_dict[t[0]]:
            if relation == "dayperiod":
                continue
            nodes_relation_dict[t[0]][relation] = 0

        nodes_relation_dict[t[0]][relation] += 1


#Sort the concepts for each span by their frequency
for span, concepts in nodes_relation_dict.iteritems():
    nodes_relation_dict[span] = OrderedDict(sorted(concepts.items(), key=lambda concepts: concepts[1], reverse=True)).items()

print_to_file = 1
if print_to_file:
    for span, concepts in nodes_relation_dict.iteritems():
        print span, concepts

pickle.dump(nodes_relation_dict, open("nodes_relation_dict.p", "wb"))
