import sys, os
import cPickle as pickle
import time
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

if not os.environ.has_key('VW_PYTHON_PATH'):
	print "Please set the env var VW_PYTHON_PATH to point to location of vowpal_wabbit/python"
	sys.exit()	
VW_PYTHON_PATH = os.environ['VW_PYTHON_PATH']
sys.path.append(VW_PYTHON_PATH)

import pyvw

class Span:
	def __init__(self, words, pos, concept="NULL", parents=[]):
		self.words = words.lower()
		self.pos = pos
		self.concept = concept
		self.parents = parents
	def __str__(self):
		return repr(self)
	def __repr__(self):
		return self.words
    
def getKbestConcepts(span, span_concept_dict=None, vnpb_words_concepts_dict=None):
	#Get the top k concepts aligned with span.words
	K = 5
	if span_concept_dict is None: span_concept_dict = pickle.load(open("data/amr-release-1.0-training-bolt/span_concept_dict.p", "rb"))
	if span_concept_dict.has_key(span.words):
		return [ (concept, count) for (concept, count) in span_concept_dict[span.words]][:K]
	if vnpb_words_concepts_dict is None: vnpb_words_concepts_dict = pickle.load(open("vnpb_words_concepts_dict.p", "rb"))
	if vnpb_words_concepts_dict.has_key(span.words):
		#print "Found in vnpb"
		return [ (concept, 1) for concept in vnpb_words_concepts_dict[span.words]]
	#if span.words in stopwords.words('english'):
	#	return [("NULL", 1)]
	stemmer=PorterStemmer()
	span_stem = stemmer.stem(span.words)
	if span.pos[0] == "V":
		return [("NULL", 1), (str(span_stem)+"-01", 1)]
	return [("NULL", 1), (str(span_stem), 1)]

concept_labels = {"NULL": 1}
last_used_label = 1

def concept2label(concept):
	global concept_labels
	global last_used_label
	if not concept_labels.has_key(concept):
		concept_labels[concept] = last_used_label + 1
		last_used_label += 1
	return concept_labels[concept]  

def label2concept(_label):
	global concept_labels
	for concept, label in concept_labels.iteritems():
		if label == _label:
			return concept

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
	return concept.split('-')

class Concept_Learning(pyvw.SearchTask):
	def __init__(self, vw, sch, num_actions):
		pyvw.SearchTask.__init__(self, vw, sch, num_actions)
		sch.set_options( sch.AUTO_HAMMING_LOSS | sch.IS_LDF | sch.AUTO_CONDITION_FEATURES )
		self.span_concept_dict = pickle.load(open("data/amr-release-1.0-training-bolt/span_concept_dict.p", "rb"))
		self.vnpb_words_concepts_dict = pickle.load(open("vnpb_words_concepts_dict.p", "rb"))

	def makeExample(self, sentence, i, concept, count, index):
		length = 1
		is_best = 0
		if index == 0:
			is_best = 1
		f = lambda: \
			{
				's': [ 'w=' + '_'.join([span.words for span in sentence[i:i+length]])]
				 + ['p=' + '_'.join([span.pos for span in sentence[i:i+length]]) ]
				 + [ "bow=" + span.words for span in sentence[i:i+length] ]
				 + [ "bop=" + span.pos for span in sentence[i:i+length] ]
				 + [ "w@-" + str(delta) + "=" + get_words(sentence,i-delta) for delta in [1,2] ]
				 + [ "w@+" + str(delta) + "=" + get_words(sentence,i+length+delta-1) for delta in [1,2] ]
				 + [ "p@-" + str(delta) + "=" + get_pos(sentence,i-delta) for delta in [1,2] ]
				 + [ "p@+" + str(delta) + "=" + get_pos(sentence,i+length+delta-1) for delta in [1,2] ] 
				 + [ "boc=" + concept for (concept, count) in getKbestConcepts(sentence[i], self.span_concept_dict, self.vnpb_words_concepts_dict)] 
				,
				'c': get_concept_features(concept) + ['count=' + str(count)] + [is_best]
			}
		#f = {}
		ex = self.example(f, labelType=self.vw.lCostSensitive)
		label = concept2label(concept)
		ex.set_label_string(str(label) + ":0")
		return ex

	def predict_concept(self, sentence, i):
		span = sentence[i]
		k_best_concepts = getKbestConcepts(sentence[i], self.span_concept_dict, self.vnpb_words_concepts_dict)
		examples = [self.makeExample(sentence, i, concept, count, v) for v,(concept, count) in enumerate(k_best_concepts)]
		oracle = [ v for v,(concept, count) in enumerate(k_best_concepts)  if concept == span.concept ]
		pred = self.sch.predict(examples = examples,
								my_tag = i+1,
								oracle = oracle,
								condition = [(i,'p'), (i-1,'q')]
							)
		return concept2label(k_best_concepts[pred][0])

	def _run(self, sentence):
		#print [span.words for span in sentence]
		output = []
		for i in range(len(sentence)):
			span = sentence[i]
			#print span.words
			k_best_concepts = getKbestConcepts(sentence[i], self.span_concept_dict, self.vnpb_words_concepts_dict)
			examples = [self.makeExample(sentence, i, concept, count, v) for v,(concept, count) in enumerate(k_best_concepts)]
			oracle = [ v for v,(concept, count) in enumerate(k_best_concepts)  if concept == span.concept ]
			pred = self.sch.predict(examples = examples,
			                        my_tag = i+1,
			                        oracle = oracle,
                                    condition = [(i,'p'), (i-1,'q')]
									)
			output.append( concept2label(k_best_concepts[pred][0]) )
		return output

	def predictOneBest(self, sentence):
		#print [span.words for span in sentence]
		output = []
		for i in range(len(sentence)):
			span = sentence[i]
			#print span.words
			k_best_concepts = getKbestConcepts(sentence[i], self.span_concept_dict, self.vnpb_words_concepts_dict)
			pred = 0
			output.append( concept2label(k_best_concepts[pred][0]) )
		return output

def get_true_labels(sentence):
	return [concept2label(span.concept) for span in sentence]

def print_comparison(predicted, true):
	for i in range(len(predicted)):
		print label2concept(predicted[i]), label2concept(true[i])
		#if label2concept(predicted[i]) != label2concept(true[i]):
		#	print label2concept(predicted[i]), label2concept(true[i])
	print

def get_accuracy(predicted, true):
	correct_predictions = 0
	for i in range(len(predicted)):
		if predicted[i] == true[i]:
			correct_predictions += 1
	return correct_predictions*1.0/len(predicted)

def get_confusion_matrix(overall_spans, overall_predicted, overall_true, span_concept_dict, vnpb_words_concepts_dict):
	#[[true=most_freq, true!=most_freq][true=predicted, true!=predicted]]
	m = [[0, 0], [0, 0]]
	for i in range(len(overall_spans)):
		k_best_concepts = getKbestConcepts(overall_spans[i], span_concept_dict, vnpb_words_concepts_dict)
		if k_best_concepts[0][0] == label2concept(overall_true[i]):
			if overall_true[i] == overall_predicted[i]:
		 		m[0][0] += 1
		 	else:	
				m[1][0] += 1
		else:
		 	if overall_true[i] == overall_predicted[i]:
				m[0][1] += 1
			else:
				m[1][1] += 1
	return m

def main(argv):
	#Format of concept_training_dataset
	#concept_training_dataset = {id: [span, pos, concept]}
	concept_training_dataset = pickle.load(open("data/amr-release-1.0-training-bolt/concept_training_dataset.p", "rb")) 
	training_sentences = []
	for id, concept_training_data in concept_training_dataset.iteritems():
		training_sentence = []
		for [span, pos, concept] in concept_training_data:
			training_sentence.append(Span(span, pos, concept))
		training_sentences.append(training_sentence)
	N = len(training_sentences)
	#N = 10
	vw = pyvw.vw("--search 0 --csoaa_ldf m --quiet --search_task hook --ring_size 2048 -q sc -b 25 --search_alpha 1e-10 --search_rollout none")
	#vw = pyvw.vw("--search 0 --csoaa_ldf m --quiet --search_task hook --ring_size 2048 -q sc -b 25 --search_alpha 1e-10")
	task = vw.init_search_task(Concept_Learning)
	print "Learning.."
        print N
	start_time = time.time()
	#print training_sentences[:N]
	for p in range(10):
		task.learn(training_sentences[:N])
	print "Time taken: " + str(time.time() - start_time)
	concept_test_dataset = pickle.load(open("data/amr-release-1.0-test-bolt/concept_test_dataset.p", "rb"))
	test_sentences = []
	for id, concept_test_data in concept_test_dataset.iteritems():
		test_sentence = []
		for [span, pos, concept] in concept_test_data:
			test_sentence.append(Span(span, pos, concept))
		test_sentences.append(test_sentence)
	#test_sentences = test_sentences[:5]
	#test_sentences = training_sentences[:N]
	#test_sentences = training_sentences[N:]
	#test_sentences = training_sentences[int(N*0.9):]
	start_time = time.time()
	print "Testing.."
	print len(test_sentences)
	accuracy = 0 
	overall_spans = []
	overall_predicted = []
	overall_true = []
	for test_sentence in test_sentences:
		predicted = task.predict(eraseAnnotations(test_sentence))
		#predicted = task.predictOneBest(eraseAnnotations(test_sentence))
		true =  get_true_labels(test_sentence)
		#print_comparison(predicted, true)
		#accuracy += get_accuracy(predicted, true)
		overall_spans += test_sentence
		overall_predicted += predicted
		overall_true += true
	#accuracy = accuracy/len(test_sentences)
	print "Time taken: " + str(time.time() - start_time)
	overall_accuracy = get_accuracy(overall_predicted, overall_true)
	span_concept_dict = pickle.load(open("span_concept_dict.p", "rb"))
	vnpb_words_concepts_dict = pickle.load(open("vnpb_words_concepts_dict.p", "rb"))	
	overall_confusion_matrix = get_confusion_matrix(overall_spans, overall_predicted, overall_true, span_concept_dict, vnpb_words_concepts_dict)
	print "Overall"
	print "Accuracy: ", overall_accuracy
	print "Confusion matrix ([true=most_freq, true!=most_freq][true=predicted, true!=predicted])"
	print overall_confusion_matrix	
	print

	seen_spans = []
	seen_predicted = []
	seen_true = []
	unseen_spans = [] 
	unseen_predicted = []
	unseen_true = []
	for i in range(len(overall_spans)):
		if span_concept_dict.has_key(overall_spans[i].words): 
			seen_spans.append(overall_spans[i])
			seen_predicted.append(overall_predicted[i])
			seen_true.append(overall_true[i])
		else:
			unseen_spans.append(overall_spans[i])
			unseen_predicted.append(overall_predicted[i])
			unseen_true.append(overall_true[i])

	if len(seen_predicted):
		seen_accuracy = get_accuracy(seen_predicted, seen_true)
	else:
		seen_accuracy = 0
	seen_confusion_matrix = get_confusion_matrix(seen_spans, seen_predicted, seen_true, span_concept_dict, vnpb_words_concepts_dict)
	print "Seen"
	print "Accuracy: ", seen_accuracy
	print "Confusion matrix ([true=most_freq, true!=most_freq][true=predicted, true!=predicted])"
	print seen_confusion_matrix
	print

	if len(unseen_predicted):
		unseen_accuracy = get_accuracy(unseen_predicted, unseen_true)
	else:
		unseen_accuracy = 0
	unseen_confusion_matrix = get_confusion_matrix(unseen_spans, unseen_predicted, unseen_true, span_concept_dict, vnpb_words_concepts_dict)
	print "unseen"
	print "Accuracy: ", unseen_accuracy
	print "Confusion matrix ([true=most_freq, true!=most_freq][true=predicted, true!=predicted])"
	print unseen_confusion_matrix
	print

if __name__ == "__main__":
	main(sys.argv[1:])
