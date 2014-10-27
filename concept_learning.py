import os, sys

VW_PYTHON_PATH = os.environ['VW_PYTHON_PATH']
if not VW_PYTHON_PATH:
	print "Please set the env var VW_PYTHON_PATH to point to location of vowpal_wabbit/python"
	sys.exit()	
sys.path.append(VW_PYTHON_PATH)
import pyvw

class Span:
	def __init__(self, words, pos, concept="NULL", parents=[]):
		self.words = words
		self.pos = pos
		self.concept = concept
		self.parents = parents
		
training_sentence = [
	Span("Establishing", "VBG", "establish-01"),
	Span("Models", "NNS", "model", [0]),
	Span("in", "IN"),
	Span("Industrial", "NNP", "industry", [1]),
	Span("Innovation", "NNP", "innovate-01", [3])
]

def getKbestConcepts(span):
	#Get the top k concepts aligned with span.words
	return ["NULL", "establish-01", "model", "industry", "innovate-01"]

concept2label = {
	"NULL": 1,
	"establish-01" : 2,
	"model" : 3,
	"industry" : 4,
	"innovate-01" : 5,
}	

def get_words(sentence, i): 
	return "<s>" if i < 0 else "</s>" if i >= len(sentence) else sentence[i].words

def get_pos(sentence, i): 
	return "<s>" if i < 0 else "</s>" if i >= len(sentence) else sentence[i].pos

def eraseAnnotations(sentence):
    erasedSentence = []
    for i in range(len(sentence)):
        erasedSentence.append( Span(sentence[i].words, sentence[i].pos) )
    return erasedSentence

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
                   [ "p@+" + str(delta) + "=" + get_pos(sentence,i+length+delta-1) for delta in [1,2] ],
              'c': [ 'concept=' + concept ]
            }
		#print f
		ex = self.vw.example(f, labelType=self.vw.lCostSensitive)
		label = concept2label[concept]
		ex.set_label_string(str(label) + ":0")
		return ex

	def _run(self, sentence):
		output = []
		for i in range(len(sentence)):
			span = sentence[i]
			k_best_concepts = getKbestConcepts(span)
			#print "Concepts: ", k_best_concepts 
			examples = [self.makeConceptExample(sentence, i, concept) for concept in k_best_concepts]
			oracles = [concept2label[span.concept] for concept in k_best_concepts]
			pred = self.sch.predict(examples = examples,
									my_tag = 0,
									oracle = oracles)
			#print concept2label[span.concept], pred
			output.append(pred)
		#print output
		return output

def main(argv):
	vw = pyvw.vw("--search 0 --csoaa_ldf m --quiet --search_task hook --ring_size 2048 --search_no_caching -q sc")
	task = vw.init_search_task(Concept_Relation)
	for p in range(2): task.learn([training_sentence].__iter__)
	print 'test time'
	print task.predict(eraseAnnotations(training_sentence))
	print "should have printed [2, 3, 1, 4, 5]"	

if __name__ == "__main__":
	main(sys.argv[1:])

