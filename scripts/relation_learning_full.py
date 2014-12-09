import time

__author__ = 'yogarshi'

import os
import sys
import cPickle as pickle

#if not os.environ.has_key('VW_PYTHON_PATH'):
#    print "Please set the env var VW_PYTHON_PATH to point to location of vowpal_wabbit/python"
#    sys.exit()
VW_PYTHON_PATH = '/Users/yogarshi/Documents/vowpal_wabbit_hal/vowpal_wabbit/python/'
sys.path.append(VW_PYTHON_PATH)

import pyvw


class Relation:
    def __init__(self, parent, child, label="NULL", parent_pos=None, child_pos=None, parent_idx=-1, child_idx=-1,
                 dep_rel="NA"):
        self.parent = parent
        self.child = child
        self.label = label
        self.parent_pos = parent_pos
        self.child_pos = child_pos
        self.parent_idx = parent_idx
        self.child_idx = child_idx
        self.dep_rel = dep_rel


nodes = {}
edgeLabels = {}
edgeLabelsList = []
prop_bank = {}

def evaluate_output(gold, pred):
    correct = 0
    for i in range(len(gold)):
        correct += 1 if gold[i] == pred[i] else 0
    return correct


def createExample(l, null=False):
    example = []
    post_proc = []
    out = ['and', 'or', 'name', 'multi-sentence']
    if not null:
        for each in l:
            print each[5]
            x = Relation(each[0][0], each[0][1], each[0][2], each[1], each[2], each[3], each[4], each[5])
            if each[0][0] in out:
                post_proc.append(x)
            else:
                example.append(x)
    else:
        for each in l:
            x = Relation(each[0][0], each[0][1], "NULL", each[1], each[2], each[3], each[4], each[5])
            if each[0][0] in out:
                post_proc.append(x)
            else:
                example.append(x)

    return example, post_proc


def updateSeenLabels(l):

    global edgeLabels

    for each in l:
        label = each[0][2]
        if label not in edgeLabels:
            edgeLabels[label] = len(edgeLabels) + 1
            edgeLabelsList.append(label)


def updateSeenNodes(l):

    global nodes

    for each in l:

        node1 = each[0][0]
        node2 = each[0][1]

        if node1 not in nodes:
            nodes[node1] = len(nodes) + 1
        if node2 not in nodes:
            nodes[node2] = len(nodes) + 1


def getKbestEdges(parent_node, nodes_relation_dict=None):
    #Get the top k concepts aligned with span.words
    K = 5
    #if nodes_relation_dict is None:
    #    nodes_relation_dict = pickle.load(open("nodes_relation_dict.p", "rb"))
    if nodes_relation_dict.has_key(parent_node):
        return [relation for (relation, count) in nodes_relation_dict[parent_node]][:K]
    return ["NULL"]


def get_shared_features(relations):

    d = {}
    for each in relations:
        if each.parent not in d:
            d[each.parent] = 0
        d[each.parent] += 1

    shared = ["num_concepts="+str(len(d))]

    return d,shared


class RelationLearning(pyvw.SearchTask):
    def __init__(self, vw, sch, num_actions):
        pyvw.SearchTask.__init__(self, vw, sch, num_actions)
        sch.set_options(sch.AUTO_HAMMING_LOSS | sch.IS_LDF | sch.AUTO_CONDITION_FEATURES)
        self.nodes_relation_dict = pickle.load(open("nodes_relation_dict.p", "rb"))

    def make_relation_example(self, relations, i, edge_label, shared_t):

        global prop_bank

        d, shared = shared_t

        dayperiod_terms = ['morning', 'night']

        concept1 = relations[i].parent
        concept2 = relations[i].child

        edge_label_cleaned = edge_label.split('-')

        concept1_cleaned = ((concept1.replace('_', ' ')).replace('-', ' ')).split()
        concept2_cleaned = ((concept2.replace('_', ' ')).replace('-', ' ')).split()

        pos1 = relations[i].parent_pos
        pos2 = relations[i].child_pos

        idx1 = relations[i].parent_idx
        idx2 = relations[i].child_idx

        if idx1 == -1 or idx2 == -1:
            dir_edge = 'x'
            dis = "0"
        else:
            dir_edge = 'r' if idx1 < idx2 else 'l'
            dis = str(abs(idx1 - idx2))

        prop_bank_feat = []

        if concept1 in prop_bank:
            roles = prop_bank[concept1]
            for each_role in roles:
                s = roles[each_role]
                curr_role = '_'.join(s)
                prop_bank_feat.append(curr_role)


        f = {'a': #shared +
                  ['c1=' + concept1] +
                  ['c2=' + concept2] +
                  ["pos1=" + pos1] +
                  ["pos2=" + pos2] +
                  ["dir=" + dir_edge] +
                  ["dis=" + dis] +
                  ["c1c=" + x for x in concept1_cleaned if x.isalnum()] +
                  ["c2c=" + x for x in concept2_cleaned if x.isalnum()] +
                  ["polarity=" + ("T" if concept2 is '-' else "F")] +
                  ["num2=" + (str(len(concept2)) if concept2.isdigit() else "0")] +
                  ["num1=" + (str(len(concept1)) if concept1.isdigit() else "0")] +
                  ["theta0=" + (prop_bank_feat[0] if len(prop_bank_feat) > 0 else "")] +
                  #["isdayperiod=" + ("T" if concept2 in dayperiod_terms else "F")] +
                  ["deprel=" + relations[i].dep_rel],
                  #["theta1=" + (prop_bank_feat[1] if len(prop_bank_feat) > 1 else "")] +
                  #["theta2=" + (prop_bank_feat[2] if len(prop_bank_feat) > 2 else "")],
                  #["num_others=" + (str(d[concept1]) if pos1[0] == "V" else "0")],  #Testing this
                  #["optype=" + ("T" if concept1 in op_list else "F" )],

             'l': ["l=" + edge_label] + ["lc=" + x for x in edge_label_cleaned if x.isalpha()]}

        ex = self.vw.example(f, labelType=self.vw.lCostSensitive)
        #print edge_label
        label = edgeLabels[edge_label]
        ex.set_label_string(str(label)+":0")
        return ex

    def _run(self, relations):
        output = []
        #shared = get_shared_features(relations)
        shared = ([],[])
        for i in range(len(relations)):
            curr_relation = relations[i]
            k_best = getKbestEdges(curr_relation.parent, self.nodes_relation_dict)
            if k_best[0] == "NULL":
                k_best = edgeLabelsList
            #print k_best
            examples = [self.make_relation_example(relations, i, edge_label, shared) for edge_label in k_best]
            # oracle = concept2label[span.concept]
            oracle = [v for v, _label in enumerate(k_best) if _label == curr_relation.label]
            # print oracle
            pred = self.sch.predict(examples=examples,
                                    my_tag=i,
                                    oracle=oracle,
                                    )#condition=[(i, 'p'), (i-1, 'q')])
            #print pred
            #if pred!= oracle[0]:
            #    print curr_relation.parent, curr_relation.child, curr_relation.label
            #print pred
            #print k_best
            output.append(edgeLabels[k_best[pred]])
        #print output
        return output


def main(argv):

    global edgeLabels
    global prop_bank

    #Load and prepare all the daya
    training_data_p = argv[0]
    training_data = pickle.load(open(training_data_p, 'rb'))

    training_examples = []
    training_examples_clean = []
    training_examples_pp = []

    test_data_p = argv[1]
    test_data = pickle.load(open(test_data_p, 'rb'))

    prop_bank = pickle.load(open('prop_bank.p', 'rb'))

    test_examples = []
    test_examples_clean = []
    test_examples_pp = []

    for each_id in training_data:
        unprocessed_example = training_data[each_id]

        te, pp = createExample(unprocessed_example, False)
        te_clean, pp_clean = createExample(unprocessed_example, True)

        training_examples.append(te)
        training_examples_clean.append(te_clean)
        training_examples_pp.append(pp)

        updateSeenLabels(unprocessed_example)
        updateSeenNodes(unprocessed_example)


    test_data_ids = []
    for each_id in test_data:
        test_data_ids.append(each_id)
        unprocessed_example = test_data[each_id]

        te, pp = createExample(unprocessed_example, False)
        te_clean, pp_clean = createExample(unprocessed_example, True)

        test_examples.append(te)
        test_examples_clean.append(te_clean)
        test_examples_pp.append(pp)

        updateSeenLabels(unprocessed_example)
        updateSeenNodes(unprocessed_example)

    #Load the dep_parse info
    #dep_parse_train = pickle.load(open(argv[2], 'rb'))
    #dep_parse_test = pickle.load(open(argv[3], 'rb'))


    print len(training_examples)
    print len(test_examples)
    print len(test_examples_clean)
    #VW Stuff
    start = time.clock()
    print "train time"
    vw = pyvw.vw("--search 0 -b 25 --csoaa_ldf m --search_task hook --ring_size 8192 --search_no_caching -q al")
    task = vw.init_search_task(RelationLearning)

    #Train
    #N = len(training_examples)
    #print N
    #N = 2
    for p in range(1):
        print "round"
        task.learn(training_examples)

    finish = time.clock() - start

    print "Time taken to train (in s) : " + str(finish)

    ferror = open("Error.txt", 'w')
    error_dict = {}
    #Test
    print 'test time'
    correct = 0
    total = 0
    for i in range(len(test_examples)):
        pred = task.predict(test_examples_clean[i])
        pred_out = [edgeLabelsList[x-1] for x in pred]

        gold = []
        gold_out = []
        for each in test_examples[i]:
            l = each.label
            gold.append(edgeLabels[l])
            gold_out.append((each.parent, each.child, each.parent_pos, each.child_pos, each.parent_idx, each.child_idx,
                             l))


        #Add the post_processing stuff
        to_do = test_examples_pp[i]
        multi_sent = [x for x in to_do if x.parent == "multi-sentence"]
        child_ids = sorted([(x.child_idx, x.label) for x in multi_sent])

        count = 1
        for each in child_ids:
            label = each[1]
            gold.append(label)
            gold_out.append((each[0], each[1]))
            pred.append("snt" + str(count))
            pred_out.append((each[0], each[1]))

            count += 1

        and_op = [x for x in to_do if x.parent == "and"]
        child_ids = sorted([(x.child_idx, x.label) for x in and_op])

        count = 1
        for each in child_ids:
            label = each[1]
            gold.append(label)
            gold_out.append((each[0], each[1]))
            pred.append("op" + str(count))
            pred_out.append("op" + str(count))

            count += 1

        #Same deal with and

        print gold
        print pred

        ferror.write(str(test_data_ids[i]))
        ferror.write('\n')
        ferror.write(str(gold_out))
        ferror.write('\n')
        ferror.write(str(pred_out))
        ferror.write('\n')
        ferror.write('###################################\n\n')

        for j in range(len(gold_out)):
            if gold_out[j][-1] != pred_out[j]:
                t = (gold_out[j][-1], pred_out[j])
                if t not in error_dict:
                    error_dict[t] = 0
                error_dict[t] += 1

        correct += evaluate_output(gold, pred)
        total += len(gold)

    ferror.close()

    accuracy = float(correct)/float(total)
    print "Accuracy = " + str(accuracy)

    list_d = sorted([(error_dict[key], key) for key in error_dict], reverse=True)

    ferror = open("Errors_list.txt", 'w')

    for each in list_d:
        ferror.write(str(each[1]))
        ferror.write('\t')
        ferror.write(str(each[0]))
        ferror.write('\n')

    ferror.close()



if __name__ == "__main__":
    main(sys.argv[1:])