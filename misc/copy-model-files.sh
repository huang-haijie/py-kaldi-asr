#!/bin/bash
# Example script for copying model files from recipe folder to
# model folder which can be loaded by py-kaldi-asr.
# You may run find-model-files.sh to get the paths of the required files
# and modify the below scripts accordingly.

if [ $# -ne 2 ]; then
    echo "Usage: $0 <recipe_dir> <model_dir>"
    exit 1
fi

src=$1
dst=$2

mkdir -p $dst/conf
mkdir -p $dst/model/graph/phones
mkdir -p $dst/extractor
mkdir -p $dst/ivectors_test_hires/conf

cp $src/conf/mfcc_hires.conf $dst/conf/
cp $src/exp/nnet3_cleaned/ivectors_train_960_cleaned_sp_hires/conf/online_cmvn.conf $dst/conf/
cp $src/exp/nnet3_cleaned/ivectors_train_960_cleaned_sp_hires/conf/splice.conf $dst/ivectors_test_hires/conf/
cp $src/exp/chain_cleaned/tdnn_1d_sp/final.mdl $dst/model/
cp $src/data/lang_chain/words.txt $dst/model/graph/
cp $src/exp/chain_cleaned/tdnn_1d_sp/graph_tgsmall/HCLG.fst $dst/model/graph/
cp $src/exp/chain_cleaned/tdnn_1d_sp/graph_tgsmall/phones/align_lexicon.int $dst/model/graph/phones/
cp $src/exp/nnet3_cleaned/extractor/final.mat $dst/extractor/
cp $src/exp/nnet3_cleaned/extractor/final.dubm $dst/extractor/
cp $src/exp/nnet3_cleaned/extractor/final.ie $dst/extractor/
cp $src/exp/nnet3_cleaned/extractor/global_cmvn.stats $dst/extractor/

cnt=$(find $dst -type f |wc -l)
echo "$cnt files copied. Expected 11."
exit 0
