#!/bin/bash
INPUT=../data/too_big/all_games_filtered.edgelist
MODE=DenseOTF
DIM=16
P=1

Q=0.5
OUTPUT=../data/too_big/all_games_homophily.emb

# The first example in the node2vec les miserables network
pecanpy --input $INPUT --outpu $OUTPUT --mode $MODE --dimensions $DIM --p $P --q $Q --directed --weighted 

Q=2
OUTPUT=../data/too_big/all_games_structural_equivalence.emb

# The second example in the node2vec les miserables network
pecanpy --input $INPUT --outpu $OUTPUT --mode $MODE --dimensions $DIM --p $P --q $Q --directed --weighted 
