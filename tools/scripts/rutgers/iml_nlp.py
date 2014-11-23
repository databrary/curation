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

def nameFromTree(tree):

    name_from_tree = ' '.join([i[0] for i in tree])
  
    return name_from_tree

def parseSentTree(ch_tree):

    names = []

    if type(ch_tree) is nltk.Tree:
        if ch_tree.label() == 'PERSON':


            names.append(nameFromTree(ch_tree))
        else:
            for i in ch_tree:
                names.extend(parseSentTree(i))

    return names


def chunkTextSentences(textobj):

    '''not much an improvement over word tokenization'''

    names_in_sents = {}


    for k,v in textobj.items():
        key = k
        text = v

        sents = nltk.sent_tokenize(text)
        tokens = [nltk.word_tokenize(sent) for sent in sents]
        tags = [nltk.pos_tag(s) for s in tokens]
        chunked_s = nltk.ne_chunk_sents(tags)


        named_ents = []

        for ch in chunked_s:
            ents = sorted(list(set([word for tree in ch for word in parseSentTree(tree)])))

            for e in ents:
                if e not in named_ents:
                    named_ents.append(e)


        names_in_sents[key] = {'text': text, 'names': named_ents}
        
    return names_in_sents

def chunkTextWords(textobj):

    '''this is ok but still leaves a bit of a mess to clean up around the names'''

    stop_words = ['Camera', 'Cameras', 'Table', 'Tables', 'Cohort', 'Interview', 'Roving' 'Group', 'Tape', 'Schoolopoly', 'Pizza', 'Students', 'My', 'Guess', 'Rule', 'Explorer'] #lets not use so many if we can get a better tagger/chunker through training
    re_pattern = re.compile(r'[A-Z]\d?\b') #matches something like 'A', 'B', 'C2', 'B3' etc...
    names_in_texts = {}


    for k,v in textobj.items():
        key = str(k)
        text = v

        #tagged = nltk.pos_tag(text.split())
        tagged = nltk.pos_tag(nltk.word_tokenize(text))

        chunked = nltk.ne_chunk(tagged)

        names = []

        for c in chunked:
            if type(c) is nltk.Tree and c.label() == 'PERSON':
                for i in range(len(c)): #this might give back a more workable set than below
                    name = c[i][0].strip()
                    if name not in names and name not in stop_words and re.match(re_pattern, name) is None:
                        names.append(name)
                
                

                #name = ' '.join(nameFromTree(c.leaves()))
                #if name not in names:
                #    names.append(name)
                
                    

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

'''tagging and chunking options'''
tagged_texts_w = chunkTextWords(text_store)
#tagged_texts_s = chunkTextSentences(text_store)

'''output as json if you'd like'''
json_output = json.dumps(tagged_texts_w, indent=4)
print(json_output)


'''trigger getting the frequency list of proper nouns'''
#all_nnp = allUniqNNP(tagged_texts)
#print(len(all_nnp))
#pprint(all_nnp)

'''take in the CSV data and extract names from the free text box, spit out a modified copy with the names attached'''
#addNamesToOrig(input_file, tagged_texts_w)