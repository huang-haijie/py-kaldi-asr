#!/bin/bash
if [ $# -ge 1 ]; then
    dir=$1
else
    dir=.
fi

for file in mfcc_hires.conf words.txt final.mdl splice.conf \
            HCLG.fst align_lexicon.int online_cmvn.conf final.mat \
            global_cmvn final.dubm final.ie; do
    result=$(find -L $dir -iname $file)
    if [ -z "$result" ]; then
        echo "WARNING: $file is not found."
    else
        echo $result
    fi
done


