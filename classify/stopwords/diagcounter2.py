#!/usr/bin/env python3
"""
    read through report file.  For each report, for its primary diagnostic code
    (as truncated to xx characters)
    set up a counter object (unless one already exists) and count uses of 
    vocabulary words for this truncated diagnostic code.
"""
import gener as g
import numpy as np
import time

diag_len = 1

with open('vocab2-.txt') as fi:
    vocab_dict = dict()
    offset = 0
    for lin in fi:
        line = lin.strip().split()
        #if len(line) == 3:
        vocab_dict[line[0]] = offset
        offset += 1


class vcounter:
    def __init__(self, vdict, name):
        vsize = len(vdict)
        self.vtab = np.zeros((vsize,) , dtype = np.int32)
        self.vdict = vdict
        self.misses = 0
        self.name = name
        self.total = 0

    def count(self, word):
        offset = self.vdict.get(word,None)
        if offset is None:
            self.misses += 1
            return
        self.vtab[offset] += 1

    def dump(self):
        self.total = sum(self.vtab)
        with open(self.name+'.dmp','w') as df:
            print('#Out_Of_Vocab:', self.misses, 'All else:', self.total, file = df)
            for i in self.vtab:
                print(i, file = df)
        print(self.name, self.total)


diags = dict()

def newdiag(kod):
    if kod[:diag_len] not in diags:
        vc = vcounter(vocab_dict,kod[:diag_len])
        diags[kod[:diag_len]] = vc
        return vc

    else:
        return diags[kod[:diag_len]] 


def finish():
    for vc in diags.values():
        vc.dump()


def main():
    test = 1
    oldkod = None
    olddiag = None
    for ix,w in enumerate(g.wordgen(g.path)):
        kod = g.topline[1]
        if kod != oldkod:
            olddiag = newdiag(kod)
            oldkod = kod
        olddiag.count(w)
        if ix == test:
            print(time.time(), test, g.idno, len(diags))
            test += test

    finish()

if __name__ == '__main__': main()

