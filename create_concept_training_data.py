import sys
import cPickle as pickle
import networkx as nx

def traverse_depth_first(concept_nx_graph, root=None):
	node_list = []
	if root == None:
		root = nx.topological_sort(concept_nx_graph)[0]
	node_list.append(concept_nx_graph.node[root]['instance'])
	children = concept_nx_graph.successors(root)
	if not children:
		return node_list
	ordered_children = [None]*len(children)
	order = []
	for child in children:
		order.append(concept_nx_graph.node[child]['child_num'])
	diff = max(order) + 1 - len(order)
	for child in children:
		ordered_children[concept_nx_graph.node[child]['child_num'] - diff] = child
	for child in ordered_children:
		node_list.extend(traverse_depth_first(concept_nx_graph, root=child)) 
	return node_list		

def create_training_data(sentence, span_concept):
	training_data = []
	words = sentence.split()
	i = 0
	while i < len(words):
		if span_concept.has_key(str(i)):
			span_end, span, concept_nx_graph = span_concept[str(i)]
			label = "_".join(traverse_depth_first(concept_nx_graph))
			training_data.append((" ".join(span), label))
			i = int(span_end) 
		else:
			training_data.append((words[i], None))
			i += 1
	return training_data

def get_span_concept(alignment, root, amr_nx_graph, sentence):
	span_num, graph_fragments = alignment.split("|")
	span_start, span_end = span_num.split("-")
	span = sentence.split()[int(span_start):int(span_end)]
	#Create a concept networkx graph and add all nodes in graph_fragments
	concept_nx_graph = nx.DiGraph()
	for graph_fragment in graph_fragments.split("+"):
		parent, attr_dict = root, amr_nx_graph.node[root]
		for child_num in graph_fragment.split(".")[1:]:
			children = amr_nx_graph.successors(parent)
			for child in children:
				if amr_nx_graph.node[child]['child_num'] == int(child_num):
					parent, attr_dict = child, amr_nx_graph.node[child]
		concept_nx_graph.add_node(parent, attr_dict)
	#Get all edges between the nodes in graph_fragment and add those to concept_nx_graph
	nodes = concept_nx_graph.nodes()
	for i in range(len(nodes)):
		for j in range(i + 1, len(nodes)):
			if amr_nx_graph.has_edge(nodes[i], nodes[j]):
				concept_nx_graph.add_edge(nodes[i], nodes[j], amr_nx_graph.get_edge_data(nodes[i], nodes[j]))
			if amr_nx_graph.has_edge(nodes[j], nodes[i]):
				concept_nx_graph.add_edge(nodes[j], nodes[i], amr_nx_graph.get_edge_data(nodes[j], nodes[i]))
	return (span_start, [span_end, span, concept_nx_graph])			

def get_training_dataset(amr_nx_graphs):
	training_dataset = {}
	for id, value in amr_nx_graphs.iteritems():
		span_concept = {}
		[root, amr_nx_graph, sentence, alignments] = value
		for alignment in alignments.split():
			key, value = get_span_concept(alignment, root, amr_nx_graph, sentence)
			span_concept[key] = value
		training_dataset[id] = create_training_data(sentence, span_concept)
	return training_dataset

def main(argv):
	if len(argv) < 1:
		print "usage: python create_concept_training_dataset.py <path_to_amr_nx_graphs.p>"
		return
	amr_nx_graphs_pickled_file = argv[0]
	#Format of amr_nx_graphs
	#amr_nx_graphs: {id, [root, amr_nx_graph, sentence, alignment]}
	amr_nx_graphs = pickle.load(open(amr_nx_graphs_pickled_file, "rb"))
	training_dataset = get_training_dataset(amr_nx_graphs)
	#for id, training_data in training_dataset.iteritems():
	#	print id
	#	for data in training_data:
	#		print data
	#	print
	pickle.dump(training_dataset, open("concept_training_dataset.p", "wb"))

if __name__ == "__main__":
	main(sys.argv[1:])
