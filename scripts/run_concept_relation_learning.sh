#!/bin/sh

#Create Networkx graph structure from amr data. This will create the amr_nx_graphs.p file.
python amr_reader.py amr-release-1.0-training-bolt.aligned

#Aggregate all metadata for amr sentences. This will create the amr_aggregated_metadata.p file.
python aggregate_sentence_metadata.py  amr-release-1.0-training-bolt.aligned amr-release-1.0-training-bolt.sentences amr-release-1.0-training-bolt.pos amr-release-1.0-training-bolt.ner

#Create concept training datatset i.e. create concept_training_dataset.p
python create_concept_training_dataset.py amr_nx_graphs.p amr_aggregated_metadata.p

#For each span, get a list of all concepts (with their counts). This creates the span_concept_dict.p file.
python create_span_concept_dict.py concept_training_dataset.p

#Finally run the concept_relation learner.
python concept_relation.py
