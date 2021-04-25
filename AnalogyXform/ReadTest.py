#!/usr/bin/env python3
"""
    read a test output file, and write a file gnuplot
    Each included run of subs1.py has:
    beginning line with parameters
    embedding line
    number of sub-run lines
    Two summary lines:
    relation  4 ratios
              4 mean, sigma
    output line:
    embedding pinned ratio1 mean1  sigma1  ratio2...
"""
import sys

def main():

    r = [0]*4
    means = [0]*4
    sigmas = [0]*4

    if len(sys.argv) > 0:
        inpfil = open(sys.argv[1])
    else: 
        inpfil = sys.stdin
    
    prefile = True
    for lin in inpfil:
        if lin[:5] == '*****': break
        line = lin.strip().split()
        if len(line) == 0: continue
        
        if prefile and line[0] != 'start': continue
        prefile = False

        #p = line.find('Pinned:')
        p = -1
        for i,x in enumerate(line):
            if x == 'Pinned:':
                p = i
                break
        if p > -1:
            pinned = line[p+1]
            continue
        elif len(lin)>1 and line[1] == 'loaded:':
            embedding = line[0]
        elif line[0] == 'pca':
            pass
        elif line[0] == 'Holdout':
            pass
        elif line[0][0] == '(':
            pass
        elif len(line) == 5:
            relation = line[0]
            r[0] = line[1]
            r[1] = line[2]
            r[2] = line[3]
            r[3] = line[4]
        elif len(line) == 8:
            for i in range(4):
                means[i] = line[2*i]
                sigmas[i] = line[2*i+1][1:-1]

            # and that was the last line, so print for gnuplot
            print(embedding, pinned, end=' ')
            for i in range(4):
                if i == 3:
                    fin = '\n'
                else: 
                    fin = ' '
                print (r[i],means[i], sigmas[i], end=fin)
                




main()
