#!/usr/bin/env python3
"""
    read through all of the *.dmp files in some directory, and
    report anomalous distribution of vocabulary words, either too high or too 
    low.

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

threshold = 20 # smallest number of word usages we'll retain in vocab2 dict

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

"""
# following comment obsolete; build now takes two hours.
# the vocab list was used to build the .dmp files, but since that build
# takes about five hours, I continue to use it instead of rebuilding with
# the vocab2 values
vocab = list()
offset = dict()
with open("../lemmatizer/vocab.txt") as fi:
    total_uses = 0
    for ix,lin in enumerate(fi):
        line = lin.strip().split()
        if len(line) != 3:
            raise  Exception("oops")
        w,l,fs = line
        f = int(fs)
        total_uses += f
        if w not in vocab2:
            vocab.append((w,f))
            #print ('missing vocab:',w) # these turn out to be words with lemmas
                                        # but low use counts.
        else:
            vocab.append (( w,  vocab2[w])) # prefer better count
        offset[ix] = w
        maxix = ix
        """

# if we assume that each word occurred in the vocabulary according to the
# binomial distribution, then the probability of a word occurring should be
#  p ~ (f/total_uses)
#  and the 
#  variance will be total_uses(p)(1-p)

# read any *.dmp files present
            
darrays = {}
tarrays = {}
# now read through any *.dmp files in this directory.
# I should have made these files binary...
for (p, d, fs) in os.walk('../stopwords/', topdown=True, onerror=None, followlinks=False):
    for fn in fs:
        if fn[-4:] == '.dmp':
            key = fn[:-4]
            darrays[key] = dmparr = np.ndarray(shape=maxix+1, dtype= np.int32)
            totald = 0
            with open(p+fn) as fi:
                for ix,lin in enumerate(fi):
                    if ix == 0:
                        #print(lin)
                        line = lin.strip().split()
                        totald = int(line[1])  #number of words missed for Key
                        continue
                    line = lin.strip()
                    f = int(line)
                    totald += f   # add in this count
                    dmparr[ix-1] = f
            tarrays[key] = totald


# now read through all arrays again, and for each word, compare actual
# distribution with what we might expect based on vocab.txt
for k,arr in darrays.items():
    tcount = tarrays[k]
    more_list = []
    less_list = []
    for  f,(w,g) in zip(arr, vocab):
        if f < threshold: continue  # don't get excited about infrequent words
        if g < f: continue # this is impossible, of course ... if all consistent
        pf = g/vocab2Total
        expectedf = pf * tcount #g/total_uses * tcount
        stdf = math.sqrt(expectedf*(1-pf)) # math.sqrt(tcount*pf*(1-pf))
        if stdf != 0:
            zscore =  (f-expectedf)/stdf
            if zscore > 3:
                #print ('remarking on',k, w,f/tcount, g/total_uses)
                if len(more_list) < 99:
                    more_list.append((zscore, f/tcount, pf, w))
                elif len(more_list) == 99 :
                    more_list.append((zscore, f/tcount, pf,  w))
                    more_list.sort()
                elif zscore > more_list[0][0]:
                    more_list[0] = (zscore, f/tcount,pf,  w)
                    more_list.sort() # Here a bubble sort would be O(n)
                    more_list = more_list[-100:]
                #fall through on vanilla words...
                # we expect that the third clause, which sorts every time,
                # would be executed for less than 1% of words which pass
                # the first two clauses.  Compare below, which sorts whole
                # list for every interesting word.
            elif zscore < -3:
                less_list.append((zscore,f/tcount,pf, w))
                less_list.sort()
                if len(less_list) >100: less_list = less_list[:100]
                

            ## should make a list of say, 100 outstanding words, output 
            ## them; perhaps I can run a classifier based on those hundred.
            #   maybe I can make a list of 100 high freq, 100 low freq words...

    with open(k+'.more','w') as fo_more_likely:
        for z,f,p, w in more_list:
            print("%.5e %.5e %.5e "%(z,f,p),w , file = fo_more_likely)

    with open(k+'.less','w') as fo_less_likely:
        for z,f,p,w in less_list:
            print("%.5e %.5e %.5e "%(z,f,p),w , file = fo_less_likely)






