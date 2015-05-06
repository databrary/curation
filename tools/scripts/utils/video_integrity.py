from subprocess import PIPE, Popen
import os, sys
import time

'''For now should run from utils folder so logs get deposited correctly'''

FILE_DIR = sys.argv[1] if not sys.argv[1].endswith('/') else sys.argv[1][:-1]
FFMPEG_BIN = 'ffmpeg'
LOG_FILE = FILE_DIR.split('/')[-1] + '_errors_' + str(int(time.time())) + '.log'
LOG_DIR = os.path.expanduser('~/curation_logs/')
LOG_PATH = LOG_DIR + LOG_FILE

def getFiles(path:str) -> list:
    filesList=[]
    for root, dirs, files in os.walk(path):
        for f in files:
            filesList.append(os.path.join(root, f))
    return filesList

def main():
    files = getFiles(FILE_DIR)
    with open(LOG_PATH, 'wt') as log:
        for f in files:
            command = [
                FFMPEG_BIN,
                '-v', 'error',
                '-threads', 1,
                '-i', f,
                '-f', 'null', '-'
            ]
            print("now checking %s" % f)
            p = Popen(command, stdout=PIPE, stderr=PIPE, bufsize=10**8)
            output = p.stdout.read().decode("utf-8")
            error = p.stderr.read().decode("utf-8")
            if error != '':
                log.write("Error: %s - %s\n" % (f, error))
            elif error == '':
                log.write("%s appears to be okay\n" % f)
if __name__ == '__main__':
    main()
