#!/usr/bin/python3
import nltk
import csv
import os
import sys
if sys.version_info < (3, 0):    
    reload(sys)
    sys.setdefaultencoding("utf-8")
import json
from pprint import pprint

input_file = sys.argv[1] #csv file

def hasNum(s):

    '''check if string has a number'''
    return any(i.isdigit() for i in s)


def makeSentenceDict(inputf):
    texts = {}
    removables = {'\n': ' ',
                  '\t': ' ', 
                  ':': ' ',
                  ';': ' ',     
                  '.': '', 
                  '/': ' ', 
                  '(': ' ', 
                  ')': ' ',
                  '*': '', 
                  '=': '',
                  '-': ' ',
                  '"': '',
                  ',': ' ',
                  "'s": ''}

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

        names_in_texts[key] = {'text': text, 'proper_nouns': proper_nouns}

        
    

    return names_in_texts



def allUniqNNP(taggedobj):
    '''currently creates a count frequency dictionary of all identified pronouns'''

    all_uniq_nnp = {}

    for k,v in taggedobj.items():
        proper_nouns = taggedobj[k]['proper_nouns']
        for i in range(len(proper_nouns)):
            if not hasNum(proper_nouns[i].lower()):
                nnp = proper_nouns[i].lower()
            if nnp in all_uniq_nnp:
                all_uniq_nnp[nnp] += 1
            else:
                all_uniq_nnp[nnp] = 1

                
    return all_uniq_nnp

tagged_texts = tagText(makeSentenceDict(input_file))

json_output = json.dumps(tagged_texts, indent=4)

all_nnp = allUniqNNP(tagged_texts)

print(len(all_nnp))
pprint(all_nnp)
