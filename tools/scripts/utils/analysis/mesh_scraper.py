import requests
from lxml import html

HOME = 'https://www.nlm.nih.gov/mesh/trees.html'

'''only the categories we want, with their order on the home page'''
category_map = {
    "Anatomy" : ("A", 1),
    "Organisms" : ("B", 2),
    "Analytical, Diagnostic and Therapeutic Techniques and Equipment Category": ("E", 5),
    "Psychiatry and Psychology" : ("F", 6),
    "Phenomena and Processes" : ("G", 7),
    "Disciplines and Occupations": ("H", 8),
    "Anthropology,Education,Sociology and Social Phenomena" : ("I", 9),
    "Information Science" : ("L", 12),
    "Named Groups" : ("M", 13), 
    "Health Care" : ("N", 14),
    "Publication Characteristics" : ("V", 15)
}


def get_home(url):
    page = requests.get(url)
    return html.fromstring(page.text)

def get_category_links(d):
    tree = get_home(HOME)
    for k,v in d.items():
        _xpath_base = '//div[@id="body"]/ol/li[%s]/' % (v[1])
        _xpath_li = _xpath_base + 'ul/li/text()'
        topics = [x for x in tree.xpath(_xpath_li) if x != ' ']  
        for i in topics:
            topic, tree_head = i.split(' [')
            _xpath_a = _xpath_base + 'ul/li[%s]/a[1]/@href' % (str(int(topics.index(i))+1))
            link = tree.xpath(_xpath_a)[0]
            #link = link[0].attrib('href') if link != [] else 'NA?'
            print k, '=', topic, tree_head[0:3], link

if __name__ == '__main__':
    get_category_links(category_map)