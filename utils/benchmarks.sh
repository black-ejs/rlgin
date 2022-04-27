##!/bin/bash
HANDS_TO_PLAY=10000
for PLAYER1 in br90 r d b br br50 br10 
do 
    for PLAYER2 in br90 r d b br br50 br10 
    do 
        python playGin.py ${HANDS_TO_PLAY} ${PLAYER1} ${PLAYER1}_1 ${PLAYER2} ${PLAYER2}_2 > ${PLAYER1}_vs_${PLAYER2}_${HANDS_TO_PLAY}.log
    done
done

