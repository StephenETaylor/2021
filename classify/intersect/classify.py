#!/usr/bin/env python3
"""
    the job of this program is to run through the train set, and for each 
    diagnosis with principal (partial) code k,
    determine what fraction of the reports would be correctly classified "yes".

    k is a command line parameter, corresponding to k.more and k.less files.
"""

import gener as g
import itertools as it
import math
import numpy as np
import sys
import time

start_time = time.time()
threshold = 20
#first read the base vocabulary values, 
#vocab2 = dict() # the offsets and counts of vocab2 may differ from the vocab
#vocab2Total = 0
"""
# removed 31 Jan 2022: Instead I save statistic .more/.less file
with open("../stopwords/vocab2-.txt") as fi:
    for ix,lin in enumerate(fi):
        wd,cnt = lin.rstrip('\n\r').split('\x20')
        count = int(cnt)
        vocab2Total += count
        #if count < threshold:
        #    continue
        vocab2[wd] = count
"""

def makedict(kext):
    #read the file and build a dict of exceptional words
    more = dict()
    back = []

    with open(kext) as fi:
        for offset, lin in enumerate(fi):
            line = lin.strip().split()
            z = float(line[0])
            f = float(line[1])
            p = float(line[2])
            w = line[3]
            back.append(w)
            #g = vocab2.get(w,None)
            #if g is not None:
            more[w] = (z,f,p,offset)
            electors = np.zeros(shape=(len(more),4),dtype= np.int32)
    return more, electors, back


def main():
    # tiny UI
    if len(sys.argv) > 1 and sys.argv[1] != '-':
        k = sys.argv[1] # key name, 
    else:
        k = 'A'
    if len(sys.argv) > 2 and sys.argv[2]!= '-':
        alpha = float(sys.argv[2])  # maximum zscore to consider
    else:
        alpha = 3
    if len(sys.argv) > 3 and sys.argv[3] != '-':
        beta = float(sys.argv[3]) # minimum % change
    else:
        beta = 0
    if len(sys.argv) > 4 and sys.argv[4] != '-':
        gamma = int(sys.argv[4])
    else:
        gamma = 2000  # number of reports to process


    print ('looking at diagnoses',k)
    print(time.time() - start_time)
    more,melectors,moreback = makedict(k+'.more')
    print(time.time() - start_time)
    less,lelectors,lessback = makedict(k+'.less')

    print(time.time() - start_time)
    reports_processed = 0
    scores = [0]*4
    #read through the report file
    klen = len(k)
    report = None   # topline[0] is report id
                    # topline[1] is principal diagnosis
    for w in g.wordgen(g.path):
        if g.topline[0] != report :
            if report is not None: # and g.topline[1][:klen] == k:
                # summarize and finish analyzing report
                votes= 0; votecnt = 0
                for v,c in wordcounts.items():
                    if v in more:
                        z,f,p,offset = more[v]
                        moreBool = True
                    elif v in less:
                        z,f,p,offset = less[v]
                        moreBool = False
                    else: continue
                    # now decide based on c the relative likelihood that 
                    # c is in the neighborhood of f*repwords
                    # or in the neighborhood of p*repwords
                    # assuming that w is binomially distributed,
                    # the most likely probability of any word of report being w
                    # is c/repwords, the mean is c, the variance is
                    # c * (repwords-c)/repwords
                    # and correspondingly for f, the probability that this 
                    # word is in a key diagnosis report
                    # and p, the probability that it is in some report
                    # for primary diagnoses, we could estimate 
                    # p & f, and p & ~f,  (the exclusive probabilities)  
                    # based on a count of the number of words in each report
                    # class, which is now stored in the .dmp files.

                    rstddev = math.sqrt(c * (repwords - c)/ repwords)
                    fspot = f*repwords
                    pspot = p*repwords
                    fstddev = math.sqrt(f*(1-f)*repwords)
                    pstddev = math.sqrt(p*(1-p)*repwords)

                    fz = abs(fspot - c)/fstddev
                    pz = abs(pspot -c)/pstddev
                    
                    # votes = votes * fz/pz # f closer than p?
                    if pz/fz-1 > beta and fz < alpha:
                        # a more patient calculation could come up with a 
                        # probabilty for the fz closer hypothesis. 
                        votes += 1
                        # track individual votes
                        if moreBool:
                            if primary_diag[:klen] == k:
                                melectors[offset,3] += 1
                            else:
                                melectors[offset,1] += 1
                        else: # not moreBool
                            if primary_diag[:klen] == k:
                                lelectors[offset,3] += 1
                            else:
                                lelectors[offset,1] += 1
                    elif fz/pz-1 > beta and pz < alpha:
                        votes += -1
                        # track individual votes
                        if moreBool:
                            if primary_diag[:klen] == k:
                                melectors[offset,0] += 1
                            else:
                                melectors[offset,2] += 1
                        else:
                            if primary_diag[:klen] == k:
                                lelectors[offset,0] += 1
                            else:
                                lelectors[offset,2] += 1

                    votecnt += 1

                if votes > 0 : 
                    #print (report, 'judged as',k,votes, votecnt)
                    #print ('principal diagnosis',primary_diag)
                    #print ('secondaries',second_diags)
                    if primary_diag[:klen] == k:
                        scores[3] += 1
                        #print ('correct-p',votes)
                    else:
                        scores[1] += 1
                        #print ('wrong',votes)
                else: 
                    if primary_diag[:klen] != k:
                        scores[0] += 1
                        #print ('correct-n',votes)
                    else:
                        scores[2] +=1
                        print ('wrong',votes)

            reports_processed +=1
            if reports_processed == gamma: break
            report = g.topline[0]
            primary_diag = g.topline[1]
            second_diags = g.topline[2]
            wordcounts = dict()
            repwords = 0
        # this is another word in the report.
        wordcounts[w] = 1 + wordcounts.get(w,0)
        repwords += 1

    print(time.time() - start_time)
    print('predicted:    wrong    correct')
    print('gt',"%5s %10i %10i"%('?',scores[0],scores[1]))
    print('gt',"%5s %10i %10i"%(k,scores[2], scores[3]))

    # report on worst word
    accuracies = np.argsort(melectors[:,1] + melectors[:,3] - 
                            melectors[:,0] - melectors[:,2])
    laccuracies = np.argsort(lelectors[:,1] + lelectors[:,3] - 
                            lelectors[:,0] - lelectors[:,2])
    with open(k+'.acc','w') as fo:
        print('#'+k+'.more', file=fo)
        for accuracy_ix in accuracies: #it.chain( accuracies[0:1], 
            #accuracies[10:11], accuracies[20:21], accuracies[30:31], 
            #accuracies[40:41], accuracies[60:61], accuracies[80:81], 
            #accuracies[-10:]):
            word = moreback[accuracy_ix]
            triple = more[word]
            print (accuracy_ix, word, 
                triple[0],triple[1], triple[2],
                'voted right', 
                melectors[accuracy_ix,1] + melectors[accuracy_ix,3],
                'voted wrong',
                melectors[accuracy_ix,0] + melectors[accuracy_ix,2],
                file=fo)

        print('#'+k+'.less', file=fo)
        for ix in laccuracies:
            word = lessback[ix]
            triple = less[word]
            print (ix, word, 
                triple[0],triple[1], triple[2],
                'voted right', 
                lelectors[ix,1] + lelectors[ix,3],
                'voted wrong',
                lelectors[ix,0] + lelectors[ix,2],
                file=fo)
                    
            
if __name__ == '__main__': main()
