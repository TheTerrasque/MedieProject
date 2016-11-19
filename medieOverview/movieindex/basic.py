import os

LIB = os.path.dirname(os.path.realpath(__file__))
MAIN = os.path.dirname(LIB)

def pj(*path):
    fullpath = os.path.join(MAIN, *path)
    dfpath = os.path.dirname(fullpath)
    if not os.path.exists(dfpath):
        os.mkdir(dfpath)
    return fullpath