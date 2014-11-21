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
import re

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
                  '"': '',
                  ',': ' ',
                  "'s": '',
                  "'": ''}
    

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

    stop_words = ['Camera', 'Cameras', 'Table', 'Tables', 'Cohort', 'Interview', 'Roving' 'Group', 'Tape', 'Schoolopoly', 'Pizza', 'Students', 'My', 'Guess', 'Rule', 'Explorer'] #lets not use so many if we can get a better tagger/chunker through training
    re_pattern = re.compile(r'[A-Z]\d?\b') #matches something like 'A', 'B', 'C2', 'B3' etc...
    names_in_texts = {}


    for k,v in textobj.items():
        key = k
        text = v

        #tagged = nltk.pos_tag(text.split())
        tagged = nltk.pos_tag(nltk.word_tokenize(text))

        chunked = nltk.ne_chunk(tagged)

        names = []

        for c in chunked:
            if type(c) is nltk.Tree and c.label() == 'PERSON':
                for i in range(len(c)):
                    name = c[i][0].strip()
                    if name not in names and name not in stop_words and re.match(re_pattern, name) is None:
                        names.append(name)
        

        names_in_texts[key] = {'text': text, 'names': names}




    return names_in_texts



def allUniqNNP(taggedobj):
    '''currently creates a count frequency dictionary of all identified proper nouns'''

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

print(json_output)
#all_nnp = allUniqNNP(tagged_texts)
#print(len(all_nnp))
#pprint(all_nnp)
