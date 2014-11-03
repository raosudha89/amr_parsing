import sys
import cPickle as pickle
import networkx as nx

def traverse_depth_first(concept_nx_graph, parent=None):
	node_list = []
	if parent == None:
		parent = nx.topological_sort(concept_nx_graph)[0]
	node_list.append(concept_nx_graph.node[parent]['instance'])
	children = []
	for child in concept_nx_graph.successors(parent):
		if concept_nx_graph.node[child]['parent'] == parent:
			children.append(child)
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
		node_list.extend(traverse_depth_first(concept_nx_graph, parent=child)) 
	return node_list		

def create_training_data(sentence, span_concept, pos_line):
	training_data = []
	words = sentence.split()
	words_pos = pos_line.split()
	i = 0
	while i < len(words):
		span_start = str(i)
		if span_concept.has_key(span_start):
			span_end, span, concept_nx_graph = span_concept[span_start]
			span_from_pos = [word_pos.split("_")[0] for word_pos in words_pos[int(span_start):int(span_end)]]
			assert(span == span_from_pos)
			pos = [word_pos.split("_")[1] for word_pos in words_pos[int(span_start):int(span_end)]]
			label = "_".join(traverse_depth_first(concept_nx_graph))
			training_data.append([" ".join(span), " ".join(pos), label])
			i = int(span_end) 
		else:
			[word_from_pos, pos] = words_pos[i].split("_")
			assert(words[i] == word_from_pos)
			training_data.append([words[i], pos, "NULL"])
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
				if amr_nx_graph.node[child]['parent'] == parent and amr_nx_graph.node[child]['child_num'] == int(child_num):
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

def get_training_dataset(amr_nx_graphs, amr_aggregated_metadata):
	training_dataset = {}
	for id, value in amr_nx_graphs.iteritems():
		span_concept = {}
		[root, amr_nx_graph, sentence, alignments] = value
		for alignment in alignments.split():
			span, concept = get_span_concept(alignment, root, amr_nx_graph, sentence)
			span_concept[span] = concept
		training_dataset[id] = create_training_data(sentence, span_concept, amr_aggregated_metadata[id][1])
	return training_dataset

def main(argv):
	if len(argv) < 2:
		print "usage: python create_concept_training_dataset.py <amr_nx_graphs.p> <amr_aggregated_metadata.p>"
		return
	amr_nx_graphs_p = argv[0]
	amr_aggregated_metadata_p = argv[1]
	#Format of amr_nx_graphs
	#amr_nx_graphs = {id : [root, amr_nx_graph, sentence, alignment]}
	amr_nx_graphs = pickle.load(open(amr_nx_graphs_p, "rb"))

	#Format of amr_aggregated_metadata
	#amr_aggregated_metadata = {id : [sentence, pos, ner]}
	amr_aggregated_metadata = pickle.load(open(amr_aggregated_metadata_p, "rb"))

	training_dataset = get_training_dataset(amr_nx_graphs, amr_aggregated_metadata)
	print_to_file = 0
	if print_to_file:
		for id, training_data in training_dataset.iteritems():
			print id
			for data in training_data:
				print data
			print
	pickle.dump(training_dataset, open("concept_training_dataset.p", "wb"))

if __name__ == "__main__":
	main(sys.argv[1:])
