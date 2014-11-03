import sys
import cPickle as pickle
from collections import OrderedDict

argv = sys.argv[1:]
if len(argv) < 1:
	print "usage: create_span_concept_dict.py <concept_training_dataset.p>"
	sys.exit()

concept_training_dataset = pickle.load(open(argv[0], "rb"))

span_concept_dict = {}

for id, concept_training_data in concept_training_dataset.iteritems():
	for [span, pos, concept] in concept_training_data:
		if span_concept_dict.has_key(span):
			if span_concept_dict[span].has_key(concept):
				span_concept_dict[span][concept] += 1
			else:
				span_concept_dict[span][concept] = 1
		else:
			span_concept_dict[span] = {concept:1}

#Sort the concepts for each span by their frequency
for span, concepts in span_concept_dict.iteritems():
	span_concept_dict[span] = OrderedDict(sorted(concepts.items(), key=lambda concepts: concepts[1], reverse=True)).items()

print_to_file = 1
if print_to_file:
	for span, concepts in span_concept_dict.iteritems():
		print span, concepts	

pickle.dump(span_concept_dict, open("span_concept_dict.p", "wb"))
