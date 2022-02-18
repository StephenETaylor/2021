#!/usr/bin/env python3
"""
    This is a third version of classify.py.  This version uses a different
    "voting"/conflict resolution technique, as well as different data,
    but in the same format as the second version.

    the job of this program is to run through the train set, and for each 
    diagnosis with principal or secondary (partial) code k,
    determine what fraction of the reports would be correctly classified "yes".

    k is a command line parameter, corresponding to k.more and k.less files.
    other command line parameters, alpha, beta, gamma, delta
     alpha -- a measure of the extremity of zscore for words
     beta  -- a proportion above 1 required for a comparison of marked/default
     gamma -- number of reports to examine
     delta -- how many words to extract from the str(k)+'.more' file
     epsilson -- if k.reject file is present, epsilon * rejectprob is threshold                 for removing word from more.
"""

import f1
import gener as g
import itertools as it
import math
import numpy as np
import sys
import time

start_time = time.time()
threshold = 20

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
    gamma = int(float(sys.argv[4])) # so 2e4 is an allowed value
else:
    gamma = 2000  # number of reports to process
if len(sys.argv) > 5 and sys.argv[5] != '-':
    delta = int(float(sys.argv[5]))
else:
    delta = 100
if len(sys.argv) > 6 and sys.argv[6] != '-':
    epsilon = (float(sys.argv[6]))
else:
    epsilon = 1e5  # that is, only a *very* extreme word would be left out 
                   # of the feature set.

sqrt2 = math.sqrt(2)

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

class lpool:
    """
    a multiset, but of limited size.  As new elements beyond the
    specified length are added, the oldest in the set are removed.
    The underlying data structure is a python list, but instead of
    using del [0]; append(), we use a rotating insertion pointer.
    (basically an overflowing fifo, but only the fi part.)
    """
    def __init__(self,length):
        self.length = length
        self.data = [None]*length
        self.next = 0

    def insert(self, x):
        self.data[self.next] = x
        self.next = (self.next + 1) % self.length

    def getlist(self):
        """
        A generator to return the items in the lpool, oldest (remaining) first
        if there were less the self.length items, or some items were None,
        we return less than length items in all
        """
        for i in range(self.length):
            retval = self.data[self.next]
            self.next = (self.next + 1) % self.length
            if retval is None: continue
            yield retval


def makedict(kext, rejects=None):
    #read the file and build a dict of exceptional words
    
    if rejects == None: rejects = set()

    pool = lpool(delta) # we specified a number of feature words in UI
    with open(kext) as fi:
        for offset, lin in enumerate(fi):
            # read and discard all but delta values from the file
            line = lin.strip().split()
            z = float(line[0])
            f = float(line[1]) # P(reports w/ word w| given labelled K)
            p = float(line[2]) # P(of w in any report)
            w = line[3]
            pk = float(line[4]) # fraction of all reports that have this label.
            if w in rejects:
                if rejects[w] > epsilon * f: continue  # reject this word
            pool.insert((z,f,p,w,pk))

    more = dict()
    back = []
    for offset,(z,f,p,w,pk) in enumerate(pool.getlist()):
        # now build the datastructures, using the data from the pool
            back.append(w)
            #g = vocab2.get(w,None)
            #if g is not None:
            more[w] = (z,f,p,offset,pk)
            electors = np.zeros(shape=(len(more),4),dtype= np.int32)
    return more, electors, back

def rejectsDict(key):
    """ 
    read the key.rejects file, if any, and return a dict, indexed by word,
    of the highest probability for that word in any peer key.
    """
    retdict = dict()
    try:
        with open(key+'.rejects') as fi:
            for lin in fi:
                line = lin.strip().split()
                w = line[3]
                p = float(line[8])
                if retdict.get(w,0) < p:
                    retdict[w] = p
        return retdict

    except:
        return retdict


def main():

    print ('looking at diagnoses',k)
    rejects = rejectsDict(k)
    more,melectors,moreback = makedict(k+'.more2', rejects=rejects)
    #print(time.time() - start_time)
    #less,lelectors,lessback = makedict(k+'.less')
    print('setup:', '%5.2f'%(time.time()-start_time), 'sec')

    reports_processed = 0
    scores = [0]*4
    #read through the report file
    klen = len(k)
    report = None   # topline[0] is report id
                    # topline[1] is principal diagnosis
                    # topline[2] is string version of list of secondary diag.
    for w in g.wordgen(g.path):
        if g.topline[0] != report :
            if report is not None: # and g.topline[1][:klen] == k:
                # summarize and finish analyzing report
                votesf = votesp = 0; votecnt = 0
                voteNo = 1
                for v,c in wordcounts.items():
                    if v in more:
                        z,f,p,offset,pk = more[v]
                        moreBool = True
                    #elif v in less:
                    #    z,f,p,offset = less[v]
                    #    moreBool = False
                    else: continue # should this be a negative vote?
                    """
                    now f is P(w|key) prob of report labeled 'key' as a w in it
                        p is P(w)  prob that any reprot has a w in it
                        pk is P(key) prob that a report is labelled 'key'

                        We want to compute P(key|w), the probability that
                        a report containing at least one occurence of w
                        has (among others) the label 'key'

                        by Bayes law we have:
                        P(key|w) = P(w|key)*P(k)/P(w)
                    """

                    pkey_w = f* pk / p

                    """
                    Combine votes by multiplying the not cases`
                    """
                    voteNo = voteNo * (1 -pkey_w)

                    if True:  #feature selection implies every vote is in favor
                        # track individual feature votes
                        if moreBool:
                            if k in rep_diags :
                                # classified correct-positive (tp)
                                melectors[offset,3] += 1
                            else:
                                # classified wrong-positive   (fp)
                                melectors[offset,0] += 1
                        else: # not moreBool
                            if k in rep_diags:
                                # classified correct, positive  (tp)
                                lelectors[offset,3] += 1
                            else:
                                # classified wrong, positive (tn)
                                lelectors[offset,0] += 1
                    else:  # this was a vote against label k
                        # track individual feature votes
                        if moreBool:
                            if k in rep_diags:
                                # wrong negative         (fn)
                                melectors[offset,2] += 1
                            else:
                                # correct negative       (tn)
                                melectors[offset,1] += 1
                        else:
                            if k in rep_diags:
                                # wrong, negative        (fn)
                                lelectors[offset,2] += 1
                            else:
                                # correct, negative      (tn)
                                lelectors[offset,1] += 1

                    votecnt += 1

                if voteNo < 0.5 :  # if true, label this report with key k
                    #print (report, 'judged as',k,votes, votecnt)
                    #print ('principal diagnosis',primary_diag)
                    #print ('secondaries',second_diags)
                    if k in rep_diags:
                        scores[3] += 1  # tp
                        #print ('correct-p',votes)
                    else:
                        scores[0] += 1  # fp
                        #print ('wrong',votes)
                else: # we label this as 'not k'
                    if k in rep_diags: # were we right?
                        scores[1] += 1  # tn
                        #print ('correct-n',votes)
                    else:
                        scores[2] +=1  # fn
                        #print ('false-negative',votes)

            reports_processed +=1
            if reports_processed == gamma: break
            report = g.topline[0]
            primary_diag = g.topline[1]
            second_diags = eval(g.topline[2])
            rep_diags = set()
            for d in it.chain(second_diags,[primary_diag]):
                rep_diags.add(d[:klen])

            wordcounts = dict()
            repwords = 0
        # this is another word in the report.
        wordcounts[w] = 1 + wordcounts.get(w,0)
        repwords += 1

    print('predicted:    wrong    correct')
    print('gt',"%5s %10i %10i"%('?'*len(k),scores[0],scores[1]))
    print('gt',"%5s %10i %10i"%(k,scores[2], scores[3]))
    fp,tn,fn,tp = scores
    f1.comp_f1( fp,tn,fn,tp, printout=True)

    # report on worst word
    accuracies = np.argsort(melectors[:,1] + melectors[:,3] - 
                            melectors[:,0] - melectors[:,2])
    #laccuracies = np.argsort(lelectors[:,1] + lelectors[:,3] - 
    #                        lelectors[:,0] - lelectors[:,2])
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

        
            """ # removing saving these words, because we are not longer considering them.
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
                """

    print('done:', '%5.2f'%(time.time()-start_time), 'sec')
                    
            
if __name__ == '__main__': main()
