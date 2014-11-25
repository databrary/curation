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
import string

input_file = sys.argv[1] #csv file


def hasNum(s):

    '''check if string has a number'''
    return any(i.isdigit() for i in s)


def makeSentenceDict(inputf):
    texts = {}
    
    punctuation = list(string.punctuation)

    with open(inputf, 'rt') as csvfile:
        f = csv.reader(csvfile)
        h = next(f)

        for row in f:
            reel_id = row[0].strip()

            if row[2].strip() != '':
                content_text = row[2].strip()

                content_text = ''.join(char for char in content_text if char not in punctuation)
                
                texts[reel_id] = content_text

    return texts

def parseTreeNames(chunk, label):

    stop_words = ['Camera', 'Cameras', 'Table', 'Tables', 'Cohort', 'Interview', 'Roving' 'Group', 'Tape', 'Schoolopoly', 'Pizza', 'Students', 'My', 'Guess', 'Rule', 'Explorer'] #lets not use so many if we can get a better tagger/chunker through training
    re_pattern = re.compile(r'[A-Z]\d?\b') #matches something like 'A', 'B', 'C2', 'B3' etc...

    entities = []

    for c in chunk: #might like to recurse if trees in trees
        if type(c) is nltk.Tree and c.label() == label:
            for i in range(len(c)): #clunky but gives a more workable set
                entity = c[i][0].strip()
                if entity not in entities and entity not in stop_words and re.match(re_pattern, entity) is None:
                    entities.append(entity)
        

    return entities



def chunkTextWords(textobj):

    '''this is ok but still leaves a bit of a mess to clean up around the names'''
    
    names_in_texts = {}


    for k,v in textobj.items():
        key = str(k)
        text = v

        #tagged = nltk.pos_tag(text.split())
        tagged = nltk.pos_tag(nltk.word_tokenize(text))

        chunked = nltk.ne_chunk(tagged)

        names = parseTreeNames(chunked, 'PERSON')
                
        names_in_texts[key] = {'text': text, 'names': names}


    return names_in_texts

def addNamesToOrig(inputf, results_dict):

    out_name = inputf.split('/')[-1].split('.')[0] + '_classified.csv'

    with open(inputf, 'rt') as in_csv:
        r = csv.reader(in_csv)
        w = csv.writer(open(out_name, 'wt'))
        header = next(r)
        header.extend(['participant_names'])
        w.writerow(header)

        for row in r:
            try:
                row.extend([results_dict[row[0]]['names']])
                w.writerow(row)
            except:
                print('passing over %s, because it must have been blank in the original' % (row))
                pass #there was one blank record in the data.


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

text_store = makeSentenceDict(input_file)

'''tagging and chunking'''
tagged_texts_w = chunkTextWords(text_store)

'''output as json if you'd like'''
json_output = json.dumps(tagged_texts_w, indent=4)
print(json_output)


'''trigger getting the frequency list of proper nouns'''
#all_nnp = allUniqNNP(tagged_texts)
#print(len(all_nnp))
#pprint(all_nnp)

'''take in the CSV data and extract names from the free text box, spit out a modified copy with the names attached'''
#addNamesToOrig(input_file, tagged_texts_w)