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
        #self.par_par =
        #self.child_child =


nodes = {}
edgeLabels = {}
edgeLabelsList = []
#prop_bank = {}
seen_in_test_p = {}
seen_in_test_c = {}

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


def updateSeenInTrain(l):

    global seen_in_test_p
    global seen_in_test_c


    for each in l:

        node1 = each[0][0]
        node2 = each[0][1]

        seen_in_test_p[node1] = 1
        seen_in_test_c[node2] = 1


def getKbestEdges(parent_node, child_node, nodes_relation_dict_out=None, nodes_relation_dict_in=None):
    #Get the top k concepts aligned with span.words
    K = 5
    #if nodes_relation_dict is None:
    #    nodes_relation_dict = pickle.load(open("nodes_relation_dict.p", "rb"))
    if parent_node in nodes_relation_dict_out:
        t1 = [relation for (relation, count) in nodes_relation_dict_out[parent_node]][:K]
    else:
        t1 = []
    if child_node in nodes_relation_dict_in:
        t2 = [relation for (relation, count) in nodes_relation_dict_in[child_node]][:K]
    else:
        t2 = []

    #t2 = []
    ret = list(set(t1 + t2))

    if len(ret) == 0:
        return ["NULL"]

    return ret




class RelationLearning(pyvw.SearchTask):

    def __init__(self, vw, sch, num_actions):
        pyvw.SearchTask.__init__(self, vw, sch, num_actions)
        sch.set_options(sch.AUTO_HAMMING_LOSS | sch.IS_LDF | sch.AUTO_CONDITION_FEATURES)
        self.nodes_relation_dict = pickle.load(open("nodes_relation_dict.p", "rb"))
        self.nodes_relation_dict_out = self.nodes_relation_dict[0]
        self.nodes_relation_dict_in = self.nodes_relation_dict[1]

    def get_shared_features(self, relations, i):

        concept1 = relations[i].parent
        concept2 = relations[i].child

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

        f = lambda : {'a': ['c1=' + concept1] + ['c2=' + concept2] +
                           ["pos1=" + pos1] + ["pos2=" + pos2] +
                           ["dir=" + dir_edge] +
                           ["dis=" + dis] +
                           ["c1c=" + x for x in concept1_cleaned if x.isalnum()] +
                           ["c2c=" + x for x in concept2_cleaned if x.isalnum()] +
                           ["polarity=" + ("T" if concept2 is '-' else "F")] +
                           ["num2=" + (str(len(concept2)) if concept2.isdigit() else "0")] +
                           ["num1=" + (str(len(concept1)) if concept1.isdigit() else "0")] +
                           ["deprel=" + relations[i].dep_rel] }
                  #["theta0=" + (prop_bank_feat[0] if len(prop_bank_feat) > 0 else "")],
                  #["isdayperiod=" + ("T" if concept2 in dayperiod_terms else "F")] +

                  #["theta1=" + (prop_bank_feat[1] if len(prop_bank_feat) > 1 else "")] +
                  #["theta2=" + (prop_bank_feat[2] if len(prop_bank_feat) > 2 else "")],
                  #["num_others=" + (str(d[concept1]) if pos1[0] == "V" else "0")],  #Testing this
                  #["optype=" + ("T" if concept1 in op_list else "F" )],

        ex = self.example(f, labelType=self.vw.lCostSensitive)
        ex.set_label_string("shared")
        return ex


    def make_relation_example(self, relations, i, edge_label):

        edge_label_cleaned = edge_label.split('-')

        concept1 = relations[i].parent
        concept2 = relations[i].child

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

        f = lambda : {'a': ['c1=' + concept1] + ['c2=' + concept2] +
                           ["pos1=" + pos1] + ["pos2=" + pos2] +
                           ["dir=" + dir_edge] +
                           ["dis=" + dis] +
                           ["c1c=" + x for x in concept1_cleaned if x.isalnum()] +
                           ["c2c=" + x for x in concept2_cleaned if x.isalnum()] +
                           ["polarity=" + ("T" if concept2 is '-' else "F")] +
                           ["num2=" + (str(len(concept2)) if concept2.isdigit() else "0")] +
                           ["num1=" + (str(len(concept1)) if concept1.isdigit() else "0")] +
                           ["deprel=" + relations[i].dep_rel],

                      'l': ["l=" + edge_label] + ["lc=" + x for x in edge_label_cleaned if x.isalpha()]}

        ex = self.vw.example(f, labelType=self.vw.lCostSensitive)
        label = edgeLabels[edge_label]
        ex.set_label_string(str(label)+":0")
        return ex

    def _run(self, relations):
        output = []
        #shared = get_shared_features(relations)
        for i in range(len(relations)):
            curr_relation = relations[i]
            k_best = getKbestEdges(curr_relation.parent, curr_relation.child,
                                   self.nodes_relation_dict_out, self.nodes_relation_dict_in)
            if k_best[0] == "NULL":
                k_best = edgeLabelsList
            if "ARG0" in k_best or "ARG1" in k_best or "ARG2" in k_best:
                if "ARG0" not in k_best:
                    k_best.append("ARG0")
                if "ARG1" not in k_best:
                    k_best.append("ARG1")
                if "ARG2" not in k_best:
                    k_best.append("ARG2")
            #shared = self.get_shared_features(relations, i)
            #print k_best
            examples = [self.make_relation_example(relations, i, edge_label) for edge_label in k_best]
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
    #global prop_bank
    global seen_in_test_c
    global seen_in_test_p

    #Load and prepare all the daya
    training_data_p = argv[0]
    training_data = pickle.load(open(training_data_p, 'rb'))

    training_examples = []
    training_examples_clean = []
    training_examples_pp = []

    test_data_p = argv[1]
    test_data = pickle.load(open(test_data_p, 'rb'))

    #prop_bank = pickle.load(open('prop_bank.p', 'rb'))

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

        updateSeenInTrain(unprocessed_example)


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


    #VW Stuff
    start = time.clock()
    print "train time"
    vw = pyvw.vw("--search 0 -b 25 --quiet --csoaa_ldf m --search_task hook --ring_size 8192 --search_no_caching -q al")
    task = vw.init_search_task(RelationLearning)

    #Train
    for p in range(1):
        print "round"
        task.learn(training_examples)

    finish = time.clock() - start

    print "Time taken to train (in s) : " + str(finish)

    #Test
    ferror = open("Error.txt", 'w')
    error_dict = {}
    print 'test time'
    correct = 0
    total = 0

    confusion_matrix = {}
    par_confusion_matrix = [[0,0], [0,0]]
    child_confusion_matrix = [[0,0], [0,0]]

    for i in range(len(test_examples)):
        pred = task.predict(test_examples_clean[i])
        pred_out = [edgeLabelsList[x-1] for x in pred]

        gold = []
        gold_out = []
        for each in test_examples[i]:
            l = each.label
            gold.append(edgeLabels[l])
            gold_out.append((each.parent, each.child, each.parent_pos, each.child_pos, each.parent_idx, each.child_idx,
                             each.dep_rel, l))


        #Add the post_processing stuff
        to_do = test_examples_pp[i]
        multi_sent = [x for x in to_do if x.parent == "multi-sentence"]
        child_ids = sorted(multi_sent, key = lambda x : x.child_idx)

        count = 1
        for each in child_ids:
            label = each.label
            gold.append(label)
            gold_out.append((each.parent, each.child, each.parent_pos, each.child_pos, each.parent_idx, each.child_idx,
                             each.dep_rel, label))
            pred.append("snt" + str(count))
            pred_out.append("snt" + str(count))

            count += 1

        #Same deal with and
        and_op = [x for x in to_do if x.parent == "and"]
        child_ids = sorted(and_op, key = lambda x : x.child_idx)

        count = 1
        for each in child_ids:
            label = each.label
            gold.append(label)
            gold_out.append((each.parent, each.child, each.parent_pos, each.child_pos, each.parent_idx, each.child_idx,
                             each.dep_rel, label))
            pred.append("op" + str(count))
            pred_out.append("op" + str(count))

            count += 1

        or_op = [x for x in to_do if x.parent == "or"]
        child_ids = sorted(or_op, key = lambda x : x.child_idx)

        count = 1
        for each in child_ids:
            label = each.label
            gold.append(label)
            gold_out.append((each.parent, each.child, each.parent_pos, each.child_pos, each.parent_idx, each.child_idx,
                             each.dep_rel, label))
            pred.append("op" + str(count))
            pred_out.append("op" + str(count))

            count += 1

        name_op = [x for x in to_do if x.parent == "name"]
        child_ids = sorted(name_op, key = lambda x : x.child_idx)

        count = 1
        for each in child_ids:
            label = each.label
            gold.append(label)
            gold_out.append((each.parent, each.child, each.parent_pos, each.child_pos, each.parent_idx, each.child_idx,
                             each.dep_rel, label))
            pred.append("op" + str(count))
            pred_out.append("op" + str(count))

            count += 1


        ferror.write(str(test_data_ids[i]))
        ferror.write('\n')
        ferror.write(str(gold_out))
        ferror.write('\n')
        ferror.write(str(pred_out))
        ferror.write('\n')
        ferror.write('###################################\n\n')

        ###EValuation


        for j in range(len(gold_out)):
            total += 1
            if gold_out[j][-1] not in confusion_matrix:
                    confusion_matrix[gold_out[j][-1]] = {}
            if pred_out[j] not in confusion_matrix[gold_out[j][-1]]:
                confusion_matrix[gold_out[j][-1]][pred_out[j]] = 0
            confusion_matrix[gold_out[j][-1]][pred_out[j]] += 1

            #Build parent and child confusion matrix
            if gold_out[j][0] in seen_in_test_p:
                p = 0
            else:
                p = 1

            if gold_out[j][1] in seen_in_test_c:
                c = 0
            else:
                c = 1



            if gold_out[j][-1] != pred_out[j]:
                t = (gold_out[j][-1], pred_out[j])
                if t not in error_dict:
                    error_dict[t] = 0
                error_dict[t] += 1
                n = 1
            else:
                correct += 1
                n = 0

            par_confusion_matrix[p][n] += 1
            child_confusion_matrix[c][n] += 1

        #correct += evaluate_output(gold, pred)
        #total += len(gold)

    ferror.close()
    accuracy = float(correct)/float(total)


    list_d = sorted([(error_dict[key], key) for key in error_dict], reverse=True)

    ferror = open("Errors_list.txt", 'w')

    for each in list_d:
        ferror.write(str(each[1]))
        ferror.write('\t')
        ferror.write(str(each[0]))
        ferror.write('\n')

    ferror.close()

    print "Total Relations predicted = " + str(total)
    print "Total Relations predicted correctly = " + str(correct)
    print "Accuracy = " + str(accuracy)



    ferror = open("Statistics.txt", 'w')

    ferror.write(str(par_confusion_matrix))
    ferror.write('\n')
    ferror.write(str(child_confusion_matrix))
    ferror.write('\n')
    ferror.write(str(confusion_matrix))

    ferror.close()






if __name__ == "__main__":
    main(sys.argv[1:])