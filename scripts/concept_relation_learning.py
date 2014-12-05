import sys, os
import cPickle as pickle
import time

if not os.environ.has_key('VW_PYTHON_PATH'):
	print "Please set the env var VW_PYTHON_PATH to point to location of vowpal_wabbit/python"
	sys.exit()	
VW_PYTHON_PATH = os.environ['VW_PYTHON_PATH']
sys.path.append(VW_PYTHON_PATH)

import pyvw

class Span:
	def __init__(self, words, pos, concept="NULL", parents=[]):
		self.words = words
		self.pos = pos
		self.concept = concept
		self.parents = parents
		
training_sentence_eg = [
	Span("Establishing", "VBG", "establish-01"),
	Span("Models", "NNS", "model", [0]),
	Span("in", "IN"),
	Span("Industrial", "NNP", "industry", [1]),
	Span("Innovation", "NNP", "innovate-01", [3])
]

def getKbestConcepts(span):
	#Get the top k concepts aligned with span.words
	K = 5
	span_concept_dict = pickle.load(open("span_concept_dict.p", "rb"))
	if span_concept_dict.has_key(span.words):
		return [ concept for (concept, count) in span_concept_dict[span.words]][:K] 
	return ["NULL"]

concept_labels = {"NULL": 1}
last_used_label = 1

def concept2label(concept):
	global concept_labels
	global last_used_label
	if not concept_labels.has_key(concept):
		concept_labels[concept] = last_used_label + 1
		last_used_label += 1
	return concept_labels[concept]  

def get_words(sentence, i): 
	return "<s>" if i < 0 else "</s>" if i >= len(sentence) else sentence[i].words

def get_pos(sentence, i): 
	return "<s>" if i < 0 else "</s>" if i >= len(sentence) else sentence[i].pos

def eraseAnnotations(sentence):
    erasedSentence = []
    for i in range(len(sentence)):
        erasedSentence.append( Span(sentence[i].words, sentence[i].pos) )
    return erasedSentence

def get_concept_features(concept):
	return [concept.split('-')]

class Concept_Relation(pyvw.SearchTask):
	def __init__(self, vw, sch, num_actions):
		pyvw.SearchTask.__init__(self, vw, sch, num_actions)
		sch.set_options( sch.AUTO_HAMMING_LOSS | sch.IS_LDF | sch.AUTO_CONDITION_FEATURES )

	def makeConceptExample(self, sentence, i, concept):
		length = 1
		f = { 's': [ 'w=' + '_'.join([span.words for span in sentence[i:i+length]]),
                     'p=' + '_'.join([span.pos for span in sentence[i:i+length]]) ] +
                   [ "bow=" + span.words for span in sentence[i:i+length] ] +
                   [ "bop=" + span.pos for span in sentence[i:i+length] ] +
                   [ "w@-" + str(delta) + "=" + get_words(sentence,i-delta) for delta in [1,2] ] +
                   [ "w@+" + str(delta) + "=" + get_words(sentence,i+length+delta-1) for delta in [1,2] ] +
                   [ "p@-" + str(delta) + "=" + get_pos(sentence,i-delta) for delta in [1,2] ] +
                   [ "p@+" + str(delta) + "=" + get_pos(sentence,i+length+delta-1) for delta in [1,2] ] +
				   [ "boc=" + c for c in getKbestConcepts(sentence[i])],
              #'c': get_concept_features(concept)
              'c': [ "concept=" + concept]
			}
		#print f
		ex = self.vw.example(f, labelType=self.vw.lCostSensitive)
		label = concept2label(concept)
		ex.set_label_string(str(label) + ":0")
		return ex

	def _run(self, sentence):
		#print [span.words for span in sentence]
		output = []
		for i in range(len(sentence)):
			span = sentence[i]
			examples = []
			oracles = []
			k_best_concepts = getKbestConcepts(sentence[i])
			#print "k_best_concepts: ", k_best_concepts
			examples = [self.makeConceptExample(sentence, i, concept) for concept in k_best_concepts]
			oracle = concept2label(span.concept)
			#for j in range(len(sentence)):
			#	k_best_concepts = getKbestConcepts(sentence[j])[:1]
			#	examples += [self.makeConceptExample(sentence, i, concept) for concept in k_best_concepts]
			#	oracles += [concept2label(span.concept) for concept in k_best_concepts]
			pred = self.sch.predict(examples = examples,
									my_tag = 0,
									oracle = oracle)
			#print concept2label(span.concept), pred
			output.append(pred)
		#print output
		return output

def get_true_concepts(sentence):
	return [concept2label(span.concept) for span in sentence]

def main(argv):
	#Format of concept_training_dataset
	#concept_training_dataset = {id: [span, pos, concept]}
	concept_training_dataset = pickle.load(open("concept_training_dataset.p", "rb")) 
	training_sentences = []
	for id, concept_training_data in concept_training_dataset.iteritems():
		training_sentence = []
		for [span, pos, concept] in concept_training_data:
			if not concept == "NULL":
				training_sentence.append(Span(span, pos, concept))
		training_sentences.append(training_sentence)
	N = int(len(training_sentences) * 0.9)
	#N = 10
	vw = pyvw.vw("--search 0 --csoaa_ldf m --quiet --search_task hook --ring_size 2048 --search_no_caching -q sc")
	if not os.path.exists("Concept_Relation_Task.p"):
		task = vw.init_search_task(Concept_Relation)
		print "Learning.."
		start_time = time.time()
		global training_sentence_eg
		for p in range(2):
			task.learn(training_sentences[:N].__iter__)
			#task.learn(training_sentences[:1].__iter__)
			#task.learn([training_sentence_eg].__iter__)
		print "Time taken: " + str(time.time() - start_time)
		#pickle.dump(task, open("concept_relation_task.p", "wb"))
	else:
		task = pickle.load(open("concept_relation_task.p", "rb"))
	test_sentences = training_sentences[N:]
	#test_sentences = training_sentences[:1]
	#test_sentences = [training_sentence_eg]
	start_time = time.time()
	print "Testing.."
	print len(test_sentences) 
	for test_sentence in test_sentences:
		print task.predict(eraseAnnotations(test_sentence))
		print "should have printed"
		print get_true_concepts(test_sentence)
	print "Time taken: " + str(time.time() - start_time)

if __name__ == "__main__":
	main(sys.argv[1:])

