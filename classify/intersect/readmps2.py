#!/usr/bin/env python3
"""
    read through all of the *.dmp2 files in some directory, and
    for each k.dmp2,  produce a file k.more2, with the property that 
    the words in k.more2 are better features for predicting that
    some report containing them is likely to have k as a primary or secondary
    diagnosis

    Number of words reported by ../lemmatizer/countdb.py:
    774421388
    This number of tokens found by the generator code.

    Number of words reported by ../lemmatizer/countfile.py
    804025900
    these are the number of tokens found by distrs3.py
"""
import math
import numpy as np
import os
import sys


threshold = 20 # smallest number of word usages we'll retain in vocab2 dict

klen = 1
morelistsize = 1000
if len(sys.argv) > 1 and sys.argv[1] != '-': morelistsize = int(sys.argv[1])
if len(sys.argv) > 2: klen = int(sys.argv[2])

#first read the vocabulary values, to make the report more readable
vocab2 = dict() # the offsets and counts of vocab2 may differ from the vocab
vocab2Total = 0
vocab = list()
offset = dict()
with open("../stopwords/vocab2-.txt") as fi:
    for ix,lin in enumerate(fi):
        wd,cnt = lin.rstrip('\n\r').split('\x20')
        count = int(cnt)
        vocab2Total += count
        #vocab2[wd] = count
        vocab2[wd] = count
        offset[wd] = ix
        vocab.append((wd,count)) # are both vocab2 and vocab useful?

maxix = len(vocab)-1

# read any *.dmp2 files present

class vcounter:
    def __init__(self, name):
        self.vtab = np.zeros((len(vocab),) , dtype = np.int32)
        self.misses = 0
        self.name = name
        self.total = 0
        self.total_reports = 0

    def load(self, fn):
        """
        load up data structure from file key.dmp2:
            first line is:
            #Out_Of_Vocab: 34368 All else: 26928271 total_reports 37271
            subsequent lines are ASCII counts aligned with vocab table
        """
        totald = 0
        with open(fn) as fi:
            for ix,lin in enumerate(fi):
                if ix == 0:
                    #print(lin)
                    line = lin.strip().split()
                    self.totald = int(line[4])
                    self.misses = int(line[1])  #number of words missed for Key
                    self.total_reports = int(line[6]) # total reports this key
                    continue
                line = lin.strip()
                f = int(line)
                self.vtab[ix-1] = f
            
darrays = {}
# now read through any *.dmp files in this directory.
# I should have made these files binary...
reports_all_keys = 0
for (p, d, fs) in os.walk('../stopwords/', topdown=True, onerror=None, followlinks=False):
    for fn in fs:
        if fn[-5:] == '.dmp2':
            key = fn[:-5]
            darrays[key] = vco = vcounter(key)
            vco.load(os.path.join(p,fn))
            reports_all_keys += vco.total_reports
    break # checkout top-level files only

# now read through all the arrays, and calculate mean and std dev for each word
sums = np.zeros((len(vocab),) , dtype = np.float32)
sums2 = np.zeros((len(vocab),) , dtype = np.float32)
count = 0
for k,vco in darrays.items():
    count += 1
    freq = vco.vtab / (vco.total_reports)
    sums += freq
    freq = freq * freq # element by element multiplication
    sums2 += freq

# calculate
means = sums / count  # make mean(f)
sums2 = sums2 / count # and sums2 E(f**2)
var  = sums2 - means * means 
sums = None # free some memory.

# now read through all keys again, and for each word, compare actual
# distribution with what we might expect based on vocab.txt
for k,vco in darrays.items():
    tcount = vco.totald
    repcount = vco.total_reports
    more_list = []
    #less_list = []
    for  ix,f,(w,g),mu,sigma2 in zip(range(len(vocab)),
                                            vco.vtab, vocab, means,var):
        if f < repcount/4: continue  # don't get excited about infrequent words
        #if g < f: continue # this is impossible, of course ... if all consistent
        fr = f/repcount # frequency of reports containing this word
        pf = mu # mu is mean of report frequencies. g/vocab2Total is global frq
        stdf = 0 if abs(sigma2) < 1e-6 else math.sqrt(sigma2) # math.sqrt(tcount*pf*(1-pf))
        if stdf != 0:
            zscore =  (fr-mu)/stdf
            if zscore > 2.0:
                #print ('remarking on',k, w,f/tcount, g/total_uses)
                if len(more_list) < morelistsize-1:
                    more_list.append((zscore, f/repcount, pf, w))
                elif len(more_list) == morelistsize-1 :
                    more_list.append((zscore, f/repcount, pf,  w))
                    more_list.sort()
                elif zscore > more_list[0][0]:
                    more_list[0] = (zscore, f/repcount,pf,  w)
                    more_list.sort() # Here a bubble sort would be O(n)
                    more_list = more_list[-morelistsize:]
                #fall through on vanilla words...
                # we expect that the third clause, which sorts every time,
                # would be executed for less than 1% of words which pass
                # the first two clauses.  

    with open(k+'.more2','w') as fo_more_likely:
        probK = vco.total_reports/reports_all_keys
        for z,f,p, w in more_list:
            print("%.5e %.5e %.5e "%(z,f,p),w , probK, file = fo_more_likely)

    #with open(k+'.less','w') as fo_less_likely:
    #    for z,f,p,w in less_list:
    #        print("%.5e %.5e %.5e "%(z,f,p),w , file = fo_less_likely)






