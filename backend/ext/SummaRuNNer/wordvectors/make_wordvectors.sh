#!/bin/bash

#### Set your hyper-parameters here ####
############## START ###################
lcode="ko" # ISO 639-1 code of target language. See `lcodes.txt`.
max_corpus_size=1000000000 # the maximum size of the corpus. Feel free to adjust it according to your computing power.
vector_size=300 # the size of a word vector
window_size=5 # the maximum distance between the current and predicted word within a sentence.
vocab_size=30000 # the maximum vocabulary size
num_negative=5 # the int for negative specifies how many “noise words” should be drawn
wiki_date=20230620
xml_name="${lcode}wiki-${wiki_date}-pages-articles-multistream.xml"
############## END #####################

echo "step 0. Make `data` directory and move there."
# mkdir data
cd data

echo "step 1. Download the stored wikipedia file to your disk."
# wget "https://dumps.wikimedia.org/${lcode}wiki/${wiki_date}/${xml_name}.bz2"

echo "step 2. Extract the bz2 file."
# bzip2 -d "${xml_name}.bz2"

cd ..
echo "step 3. Build Corpus."
python build_corpus.py --max_corpus_size=${max_corpus_size} --xml_name=${xml_name}

echo "step 4. make wordvectors"
python make_wordvectors.py --vector_size=${vector_size} --window_size=${window_size} --vocab_size=${vocab_size} --num_negative=${num_negative}

