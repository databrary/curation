import csv
import os, sys
import hashlib

_ROOTPATH = sys.argv[1]
_HOME = os.path.expanduser("~")
_OUTPUTDIR = _HOME + "/output/"
_SUFFIX = "_2"

def getFiles(path):
    filesList=[]
    for root, dirs, files in os.walk(path):
        for f in files:
            filesList.append(os.path.join(root, f))
    return filesList


def fileSize(path):
    return os.path.getsize(path)

def fileHash(path):
    fopen = open(path, 'rb').read()
    return hashlib.sha1(fopen).hexdigest()

def makeRow(path):
    e = path.split('/')
    f = e[-1]
    fp = f.split('.')
    fpath = os.path.join(e[4],e[5])
    sesh = fp[0]
    new = ".".join([(fp[0] + _SUFFIX), fp[1]]) 
    fsize = fileSize(path)
    fhash = fileHash(path)
    return [fpath, sesh, f, new, fsize, fhash]


if __name__ == '__main__':
    
    files = getFiles(_ROOTPATH)
    output = _OUTPUTDIR + "cha_files.csv"
    with open(output, "w") as f:
        w = csv.writer(f)
        head = ["path", "session", "original", "new", "size","sha1"]
        w.writerow(head)
        for f in files:
            row = makeRow(f)
            w.writerow(row)
