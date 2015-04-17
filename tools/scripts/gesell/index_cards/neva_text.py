import sys, os
from pprint import pprint

neva_file = sys.argv[1]
list_of_words = sys.argv[2:]

with open(neva_file, 'rt') as f:
    text = f.read().replace('\n\n', '||')

text_break=text.split('||')

data = []

for tb in text_break:
    parts = tb.split('\n')
    cdf_no = int(parts[0].split('#')[1].strip())
    desc = " ".join([d.strip() for d in parts[1:]]).lower() # all in lower case for search
   
    data.append({"cdfa":cdf_no, "description":desc})


count = 0
for d in data:
    ident = d['cdfa']
    text = d['description']
    if all(word in text for word in list_of_words):
        count += 1
        print("%s:\n%s" % (ident, text), '\n')
print("%s results found" % (count))