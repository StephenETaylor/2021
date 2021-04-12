#!/usr/bin/env python3
"""
    re-implement code to build xform to "fix" the analogy errors.
    for each analogy:
        1: sort out the productive pairs, parameters:
            n of acc@n, maybe 1, 3, 5,
            threshold for participates in success on left-hand side
            threshold for participates in success on right-hand side
            threshold for sum of two successes?
            [initially, want to print these for all, estimate sensible 
             starting values.]
        2: using (limited) pairs as real relation R,  held-out relation H, 
           full relation F
            number to hold out.  0 is a possibility, since unlikely even
             the pruned relation has 100% acc@1 accuracy, but will be 
             unconvincing!   
            
        3: possible PCA, P, using the two items of the (un-limited?) pairs as
           exemplars.  There aren't likely enough items to determine d**2 
           parameters for the PCA; probably not even enough for d**1.
           (maybe PCA as step 0, using original F).

        (3.5 Can I just subtract the difference space, and get a new space in
            which difference vectors are already better?)

        4: possible coordinate pruning, i.e. projection from the PCA,
            need at least two dimensions?   In Algeria paper, had good success
            with coordinates 0,1.  But these are the DIFFERENCES between 
            items, not the COMMONALITIES...  maybe.  afterwards,
            have d' dimensions

        5. difference vector variations:  
           only items in R, to average of items in R
           both ends of successful analogies from R, let search match average
           both ends of all of R
           both ends of successful analogies from F, let search match average,
            possibly bigger set than successful from R, no smaller.

        6: exact solution probably infeasible unless there a more  pairs than
           |R| >= d'**2, but training always feasible.   Random initiaization 
           may dominate for small

        7: solve or train for C, and test held-out pairs:
        compare acc@1, acc@n for R, H, R+H, F


    if I use the csls code, should have pretty quick nn-searches.
    (unfortunately, the sample embeddings I used for development are much
     bigger than the 100000 word limit built into csls [which should probably
     be reimplemented to avoid that, but isn't top priority.  And if I did,
     I'd eliminate the cache, which would slow the nn-searches back down .])
"""
#import csls
import datetime
import gensim.models as gm
import itertools as it
import math
import numpy as np
import numpy.random as npr
import plotting
import scipy.linalg as sl
import time

Language = 1 # English = 0, Arabic = 1
Eembedding = "English.w2v.bin"
Aembedding = "Arabic.w2v.bin"

# some tested with parameters: 
#   Holdout=1, accn=1, preNorm=doPCA=True, successful=1, lPr=0.25
Erelations = [
            #0 |F|=16, Pinned=# 20:.522,40:.908,50:1.012,55:1.052,60:1.08
            "relations/capital-common-countries",
            "relations/capital-world",
            "relations/city-in-state",
            "relations/country-currency",
            #4 |F|=8, Pinned = 96:.994
            "relations/family",
            "relations/gram1-adjective-adverb",
            "relations/gram2-opposite",
            "relations/gram3-comparative",
            "relations/gram4-superlative",
            "relations/gram5-present-participle",
            "relations/gram6-nationality-adjective",
            "relations/gram7-past-tense",
            #12
            "relations/gram8-plural",
            "relations/gram9-plural-verbs"]

Arelations  = [
                #0
                "Arelations/iswas.txt",
                "Arelations/noun-bil-noun.txt",
                "Arelations/noun-b-noun.txt",
                "Arelations/noun-b-noun.txt~",
                "Arelations/noun-definite.txt",
                #5
                "Arelations/noun-hA-noun-h.txt",
                "Arelations/noun-mA.txt",
                "Arelations/noun-noun-ha.txt",
                "Arelations/noun-noun-h.txt",
                "Arelations/noun-w-noun.txt",
                #10
                "Arelations/verb-she-hes.txt",
                "Arelations/verb-verb-hA.txt",
                "Arelations/verb-verb-h.txt",
                "Arelations/vheher-vhehim.txt",
                "Arelations/vheher-vsheher.txt",
                #15
                "Arelations/vheher-vshehim.txt",
                "Arelations/vheher-vshe.txt",
                "Arelations/vhehim-vsheher.txt",
                "Arelations/vhehim-vshehim.txt",
                "Arelations/vhehim-vshe.txt",
                #20
                "Arelations/vhe-vheher.txt",
                "Arelations/vhe-vhehim.txt",
                "Arelations/vhe-vsheher.txt",
                "Arelations/vhe-vshehim.txt",
                "Arelations/vhe-vshe.txt",
                #25
                "Arelations/vsheher-vshehim.txt",
                "Arelations/vshe-vsheher.txt",
                "Arelations/vshe-vshehim.txt"
              ]

embedding = [Eembedding, Aembedding][Language]
relations = [Erelations, Arelations][Language]

#parameters
numRel = None #11
accn = 1
holdout = 1
lPr = 0.25 # fraction of analogies successful = (left_prod+right_prod)/nF
preNorm = True
successful = 1 #threshold for including pair in transform goal
doPCA = True
endEarly = True

# training related:
LearningRate = 0.001
Iterations = 3001
Regularization = 0.99
Cwidth = 300
Pinned = 96 #60 

# just a format:
F3f = '%.3f'

def main():
    """
        main is guided by the global parameters, none of which is changed
    """
    if numRel is None:
        chacha = ''
    else:
        chacha = 'relation '+relations[numRel]
    print( time_check(), chacha, 'accn:', accn , 'holdout:', 
    holdout , 'lPr:', lPr , 'preNorm:', preNorm , 'successful:', successful , 
    'doPCA:', doPCA , 'Pinned:', Pinned)
    # set up language model
    wordVectors = gm.KeyedVectors.load_word2vec_format(embedding, binary = True)
    dim = wordVectors.vectors.shape[1]
    def get_index(w):
        """ gensim 4 provides a get_index, but removes vocab dict """
        return wordVectors.vocab[w].index

    vnorms = np.linalg.norm(wordVectors.vectors, axis = 1)

    print(embedding, ' loaded',time_check(),flush = True)

    # read in the relation
    if numRel is None:
        chacha = relations
    else:
        chacha = relations[numRel:] #   numRel+1]
    for Fn in chacha:
        #print('relation', Fn)
        F = []
        with open(Fn) as fi:
            for lin in fi: 
                line = lin.strip().split()
                if len(line) != 2: raise Exception("huh?")
                F .append( (line[0],line[1]) )

        nF = len(F)
        fstat = dict()

        # step1, sort out the actually productive pairs, using accn
        left_prod = [0]*nF
        right_prod = [0]*nF
        # count all successful pairs in R (either side)
        useF = [0]*nF     # set all values to "False"
        for i,(l0,l1) in enumerate(F):
            for j,(r0,r1) in enumerate(F):
                if i == j: continue # the identity analogy is too boring...
                r1int = get_index(r1)
                r1vec = wordVectors.vectors[r1int] /vnorms[r1int]

                l1int = get_index(l1)
                l0int = get_index(l0)
                r0int = get_index(r0)

                # should I normalize before adding vectors? or is afterward enough?
                if preNorm:
                    vec = (wordVectors.vectors[l1int]/vnorms[l1int] 
                        - wordVectors.vectors[l0int]/vnorms[l0int] 
                        + wordVectors.vectors[r0int]/vnorms[r0int] )
                else:
                    vec = (wordVectors.vectors[l1int]
                        - wordVectors.vectors[l0int]
                        + wordVectors.vectors[r0int] )
                vecnorm = math.sqrt((vec .dot (vec)))
                vec = vec / vecnorm
                cosVec = cosine_vecs(vec,r1vec)
                uNV = wordVectors.vectors  .dot (vec) # get the accn nearest neighbors of vec
                NV = uNV / vnorms
                cvNV = np.sort(NV)  # we don't actually care about the names ....
                # just if r1 is as close as the nth neighbor            
                if cosVec >= cvNV[-accn]: 
                    # this analogy works at specified acc@x
                    left_prod[i] += 1
                    right_prod[j] += 1
                    useF[i] += 1 # participated in a successful analogy
                    useF[j] += 1 # participated in a successful analogy
                    fstat[(l0,l1,r0)] = True
                else:
                    fstat[(l0,l1,r0)] = False

        successes1 = (sum(left_prod) + sum(right_prod))/2
        successes2 = sum(useF)/2
        if successes1 != successes2:
            raise Exception('bug')
        sr1 = successes1 / nF/(nF-1)
        usable = 0
        for i in useF:
            if i != 0:
                usable += 1
        sr2 = successes2 / usable / (usable-1)

        print(Fn,nF, usable, F3f%sr1, F3f%sr2, time_check())


        # review results and build the R+H relation
        RpH = []
        for i,pair in enumerate(F):
            success_ratio = (left_prod[i]+right_prod[i])/(nF-1) 
            if left_prod[i] > 0 and right_prod[i] > 0 and success_ratio > lPr:
                RpH.append(pair)
        score = 0
        for i,(l0,l1) in enumerate(RpH):
            for j,(r0,r1) in enumerate(RpH):
                if i==j : continue
                if fstat[(l0,l1,r0)] :
                    score += 1

        denom = len(RpH)*(len(RpH)-1)
        if denom == 0:
            sr3 = None
            print(Fn, nF,len(RpH), sr3, time_check())
        else:
            sr3 = score/denom
            print(Fn, nF,len(RpH), F3f%sr3, time_check())

        if len(RpH) < holdout +1:
            continue
        if  endEarly:
            continue
        
        baseResults = [0]*4
        testResults = [0]*4

        # now set up Relations R and H, subsets of RpH
        for c in it.combinations(range(len(RpH)),holdout):
            # do jacknife; prepare statistics for each possibility  of holdout
            R = []
            useR = [0]*(nF-holdout)
            ri = 0
            H = []
            hi = -1
            for i in c:
                while ri < i:
                    R.append(RpH[ri])
                    useR[len(R)-1] = useF[ri] # no need to recompute this
                    ri += 1
                H.append(RpH[i])
                hi = i+1
            # finish off with the end of RpH
            ri = hi
            while ri < len(RpH):
                R.append(RpH[ri])
                useR[len(R)-1] = useF[ri] # no need to recompute this
                ri += 1
            print(c, len(R), len(H))   

            # now that we have R and H, continue to compute statistics
            # for R, H, and F
           
            # set DX and DY arrays for specifying transforms.
            # use all successful pairs in R (either side) 
            xX = [] # table of indices
            for i in range(len(R)):
                if useR[i] >= successful:
                    xX.append(i)
            dX = np.ndarray((len(xX)+Pinned,dim),dtype=np.float32)
            dY = np.ndarray((len(xX)+Pinned,dim),dtype=np.float32)
            pcaD = np.ndarray((2*len(xX),dim),dtype=np.float32)
            
            #set up for PCA
            if doPCA:
                for oi,i in enumerate(xX):
                    v1int = get_index(R[i][1])
                    v0int = get_index(R[i][0])
                    v1vec = wordVectors.vectors[v1int]
                    v0vec = wordVectors.vectors[v0int]

                    pcaD[2*oi] = v0vec   # data for possible PCA
                    pcaD[2*oi+1] = v1vec

                # so compute PCA
                _,evals,PCA = plotting.PCA(pcaD, dim, mulout=False)

                #invPCA = sl.pinv(PCA)
                mvectors = wordVectors.vectors @ PCA
                mnorms = np.linalg.norm(mvectors, axis = 1)
            else:
                mvectors = wordVectors.vectors
                mnorms = vnorms
            
            # now build transform
            for oi,i in enumerate(xX):
                v1int = get_index(R[i][1])
                v0int = get_index(R[i][0])
                v1vec = wordVectors.vectors[v1int]
                v0vec = wordVectors.vectors[v0int]


                if preNorm:
                    v1vec = v1vec / vnorms[v1int]
                    v0vec = v0vec / vnorms[v0int]
                else:
                    v1vec = v1vec
                    v0vec = v0vec

                if doPCA:
                    v1vec = v1vec @ PCA
                    v0vec = v0vec @ PCA

                dX[oi] = v1vec - v0vec

            dY[:len(xX),:] = np.mean(dX[:len(xX),:], axis=0)

            bpin = len(xX)
            for i in range(bpin,bpin+Pinned): 
                # add a number of randomly chosen items to dX and dY
                # I expect to stay in the same place
                j = npr.randint(100,wordVectors.vectors.shape[0]//2)
                k = npr.randint(100,wordVectors.vectors.shape[0]//2)
                vec = wordVectors.vectors[j] - wordVectors.vectors[k]
                if doPCA:
                    vec = vec@PCA

                dX[i] = dY[i] = vec

            # train a linear transform for this relation
            C = train( dX, dX.shape[0], dY)

            mvectors = mvectors @ C
            mnorms = np.linalg.norm(mvectors,axis = 1)
            if preNorm:
                mvectors = mvectors / mnorms[:, np.newaxis]

            # now evaluate the transformed relation
            for i,(l0,l1) in enumerate(it.chain(R,H)):
                for j,(r0,r1) in enumerate(it.chain(R,H)):
                    if i == j :continue
                    l0vec = mvectors[get_index(l0)]
                    l1vec = mvectors[get_index(l1)]
                    r0vec = mvectors[get_index(r0)]
                    r1int = get_index(r1)
                    r1vec = mvectors[r1int]
                    qvec = l1vec - l0vec + r0vec

                    qvecnorm = np.linalg.norm(qvec)
                    if preNorm:
                        qvec = qvec / qvecnorm
                        qdist = cosine_vecs(qvec, r1vec)
                    else:
                        qdist = cosine_vecs(qvec/qnorm, r1vec/mnorms(r1int))

                    qvecneighbors = mvectors .dot (qvec)
                    qvecneighbors.sort()
                    if qdist >= qvecneighbors[-accn]:
                        qgood=True
                    else: 
                        qgood = False

                    # now add results into RR RH HR HH
                    # for both basecase (results in fstat)
                    # and qgood
                    offset = (i>=len(R))*1 + (j>=len(R))*2
                    baseResults[offset] += fstat[(l0,l1,r0)]*1
                    testResults[offset] += qgood*1

            print('Holdout:', c, 'testsofar', testResults, time_check())

        # done with jacknife.  Print results for relation
        print (Fn, end = ' ')
        for i in range(4):
            if i == 3:
               fin = '\n'
            else:
               fin = '\t'
            if baseResults[i] == 0:
                print(("%.3f/0"%testResults[i])+'/0', end =fin)
            else:
                print("%.3f"%(testResults[i]/baseResults[i]), end =fin)
                


            
           



           

Start = None
Last  = None
def time_check():
    """
        return string with 
            elapsed seconds since last time check and 
            total time from first call.
    """
    global Start, Last

    now = time.time()
    if Start is None:
        Start = Last = now
        return "start "+datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
    elaps = now - Last
    total = now - Start
    Last = now
    return "%2.3f %4.2f"%(elaps,total)
        



def cosine_vecs(v1,v2):
    """
    this version no longer normalizes 
    """
    prod = v1 .dot (v2)
    #normsq1 = v1 .dot(v1)
    #normsq2 = v2 .dot(v2)
    #norm = math.sqrt(normsq1 * normsq2)
    #return prod/norm
    return prod


def train(diffvec,nrel,target):
    """
        parameter diffvec is an array of difference vectors
        nrel is number of vector inthe array
        return a C array such that 
        E = diffvec @ C yields an array E == target

        a number of global values also control the training
        see (way) above
    """

    # See lengthy comment at top of program about training
    a = LearningRate   #0.0000001  # should this be a parameter?
    currentRegularization = 1-a*10
    oldgoal = None
    # initialize C in (-1,1).  Too broad?  Parameter?
    # a little tough to get the dtype and shape arguments to work...
    C = 2*np.reshape(npr.random_sample(300*Cwidth).astype(np.float32),(300,Cwidth)) - 1
    for shebang in range(Iterations):
        #E = np.ones(shape = (nrel,Cwidth, dtype=np.float32)
        E = diffvec@C  # matrix multiplication (works!)
        #Q = np.ndarray(shape=(nrel,Cwidth), dtype=np.float32)
        #bug:Q =  1-E*E  # element-wise operation: Q[i][j] = 1 - E[i][j]**2
        if shebang%100 == 0:
            # don't need to compute Q at all, just its partial derivative,
            # but want to report it every once in a while
            t = target-E # broadcast t[i][j] = target[i][j] - E[i][j]
            Q = t*t # this is elementwise, so Q[i][j] = (1-E[i][j])**2
            sss = np.sum(Q)
            mss = np.mean(Q)
            print('goal:', sss , mss ,C[0][0], shebang, a)
            # added adjustment to learning rate 7.4.2021
            if oldgoal is not None and oldgoal-sss >= 0 and abs(oldgoal-sss) < a/max(C.size,Q.size):
                a = a/2
                currentRegularization = 1-a*10
            oldgoal = sss
        #  partial d. Q_{ij} wrt C_{kj} = -2 (1-E_{ij}) * D_{ik}
        # partial d. C_{kj} wrt Q_{ij} = 1/(2*(E_{ij}-1)) / d_{ik}
        #Ct = C.T        # get transpose for below...

        # set up comparison array
        #dDelta = np.zeros(shape=(Cwidth,Cwidth), dtype=np.float32)
        #for i in range(nrel):
        #    for j in range(Cwidth):
        #        fac1 = 2*(E[i][j]-target[i][j])            #1/2/(E[i][j]-1)
                #for k in range(300): # C[k][j] changed i*j times in the nested
                                     # loops, but the changes are additions,
                                     # so the effect is the same as combining
                                     # the additions first.
                #    C[k][j] -= a*fac1*diffvec[i][k]  # was divide, -a...
        #       Ct[j] -= a*fac1*diffvec[i] # make that loop a vector operation
        #        dDelta[j] -= a*fac1*diffvec[i] # make that loop a vector operation
        Fac1 = 2*(E - target).T
        dC = a* Fac1 @ diffvec
        # moved this down:C -= dC.T
        #huh = dC+(dDelta)
        #print (np.sum(huh))
        #C += dDelta.T
        #C = Ct.T # then get back to untranposed form
        # following is the "orthogonalizing goal"
        # repeat the computation for x = y*C.t; I'm going just repeat it...

        if False: # omit orthogonalization constraint?
            E = target @ (C.T) # since Ct wasn't changed in the previous loop
            Fac1 = 2*(E-diffvec).T
            eC = a * Fac1 @ diffvec
            #C -= dC.T
            #C -= eC #.T
            C = (Regularization*C) - dC.T - eC
        else:
            # added "current" 7.4.2021
            C = (currentRegularization*C) - dC.T # don't train in orthogonalization, or regularize

        #dDelta = np.zeros(shape=(Cwidth,Cwidth), dtype=np.float32)
        #for i in range(nrel):
        #    for j in range(Cwidth):
        #        fac1 = 2*(E[i][j]-diffvec[i][j]) 
        ##       C[j] -= a*fac1*diffvec[i] # change coefficients
        #        dDelta[j] -= a*fac1*diffvec[i] # change coefficients
        #but C already transposed version of Ct
        pass
        
    return C



if __name__ == '__main__': main()            
