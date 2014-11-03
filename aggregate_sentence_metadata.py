import sys
import cPickle as pickle

argv = sys.argv[1:]
if len(argv) < 4:
	print "usage: aggregate_sentence_metadata.py <amr_file> <sentence_file> <pos_file> <ner_file>"
	sys.exit()

amr_file = open(argv[0])
sentence_file = open(argv[1])
pos_file = open(argv[2])
ner_file = open(argv[3])

amr_aggregated_metadata = {}

for amr_line in amr_file.readlines():
	if amr_line.startswith("# ::id"):
		id = amr_line.split("::")[1].strip("# ::id")
		sentence = sentence_file.readline()
		pos = pos_file.readline()
		ner = ner_file.readline()
		amr_aggregated_metadata[id] = [sentence.rstrip("\n"), pos.rstrip("\n"), ner.rstrip("\n")]
	
pickle.dump(amr_aggregated_metadata, open("amr_aggregated_metadata.p", "wb"))	
