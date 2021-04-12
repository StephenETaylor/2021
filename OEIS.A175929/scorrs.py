#!/usr/bin/env python3
"""
    experiment to see the distribution of possible spearman correlations for
    values of N items
    What is printed out here is the numerators of the product of the variations.
    the Spearman correlation is the square root of (this numerator divided
    by the largest numerator)

    Here's what I think I see so far:   It's definitely not a binomial
    distribution.  But, it is symmetrical around 0, with 
        min numerator = - max numerator
    The largest numerator is  
        sum_{-N/2 \le i\le N/2} (i-frac{N-1}{2})
      for odd N, 2* a sum of squares: for N=5, 2*(0+1+4); N=7, 2*(0+1+4+9)
      N=9, 2*(0+1+4+9+16)
    for N \ge 4, the numerator possibilities are separated by one, that is
        for odd N there are 2*maxnumerator_N + 1 possibilites in all.
    for max_numerator the count is 1, so the chance of a Spearman correlation 
        of 1 is 1/N!;  (and -1, also 1/N!)
    for max_numerator - 1, the count is N-1

    The rows of counts are the rows of the OEIS Sloane sequence A175929 
        "Triangle T(N,v)"   but it's not clear to me that the maple code
        for generating the triangle is better than the following python...

    Since there are ~2*N**3/3 entries in each row, and the sum of counts for
        the entries is N!, the average entry is 3*N!/2/N**3.  
    For N=9, the max count is 6697 (4,-4) and the central 33 are in [4954,6697];
        since max_numerator_{9} = 60, the average count should be 9!/121=2999.01
        thus the average in the center quarter is only twice the overall average

    As it happens, the code below, which loops through N! permutations, is
    too slow to finish for N\ge 13, so I'm unclear whether this phenomenon 
    continues.  Time for analysis...

"""
import itertools as it

counts = dict()
N = int(input('how many items: '))
mean = (N-1)/2
for i,p in enumerate(it.permutations(range(N))):
    tot = 0
    for j,k in zip(p,range(N)):
        tot += (j-mean)*(k-mean)
    sofar = counts.get(tot,None)
    if sofar is None:
        counts[tot] = 1
    else:
        counts[tot] = sofar+1

for k in sorted(counts.keys()):
    print (k, counts[k], end = ', ')
print()
    
