#!/bin/bash
INPUT=../data/too_big/all_games_filtered.edgelist
MODE=DenseOTF
DIM=16
P=1
Q=0.5
OUTPUT=../data/too_big/all_games_homophily.emb

pecanpy --input $INPUT --outpu $OUTPUT --mode $MODE --dimensions $DIM --p $P --q $Q --directed --weighted 