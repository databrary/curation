#!/usr/bin/python3
import nltk
import csv
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import json

input_file = sys.argv[1] #csv file

'''try with penn pos tagger'''
_POS_TAGGER = 'taggers/maxent_treebank_pos_tagger/english.pickle'

def makeSentenceDict(inputf):
    texts = {}
    removables = {'\n': ' ', ':': '', '\t': ' ', '.': ''}

    with open(inputf, 'rt') as csvfile:
        f = csv.reader(csvfile)
        h = next(f)

        for row in f:
            reel_id = row[0].strip()

            if row[2].strip() != '':
                content_text = row[2].strip()

                for k, v in removables.items():
                    if k in content_text:
                        content_text = content_text.replace(k, v)


                texts[reel_id] = content_text

    return texts



def tagText(textobj):
    names_in_texts = {}

    for k,v in textobj.items():
        key = k
        text = v

        #sentences = nltk.sent_tokenize(text)
        #tokenized_sent = [nltk.word_tokenize(sent) for sent in sentences]

        tagged = nltk.pos_tag(text.split())

        proper_nouns = [w for w, pos in tagged if pos == 'NNP']

        names_in_texts[key] = {'text': text, 'proper_nouns': tagged}

    return names_in_texts





json_output = json.dumps(tagText(makeSentenceDict(input_file)), indent=4)

print(json_output)
