#!/usr/bin/python3

from nltk.tag import pos_tag
import csv
import os
import sys
import json

input_file = sys.argv[1] #csv file


def makeSentenceDict(inputf):
    texts = {}

    with open(inputf, 'rt') as csvfile:
        f = csv.reader(csvfile)
        h = next(f)

        for row in f:
            reel_id = row[0].strip()
            content_text = row[2].strip()

            if content_text != '':
                texts[reel_id] = content_text

    return texts



def tagText(textobj):
    names_in_texts = {}

    for k,v in textobj.items():
        key = k
        text = v

        tagged = pos_tag(text.split())

        proper_nouns = [w for w, pos in tagged if pos == 'NNP']

        names_in_texts[key] = {'text': text, 'proper_names': proper_nouns}

    return names_in_texts





json_output = json.dumps(tagText(makeSentenceDict(input_file)), indent=4)

print(json_output)

            
