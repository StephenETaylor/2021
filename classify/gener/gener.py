#!/usr/bin/env python3
"""
    an attempt to rewrite the test3/distrs3 code as a generator,
    which returns words.

    on my older laptop, it takes 18 min 45 sec to read through the brno.tsv 
    file using the wordgen code.  

    The idno module variable corresponds to the line in the TSV file,
    so it increases montonically through a run.

    The topline module variable is an array which describes a report.
    IIRC, topline[0] is a report ID
          topline[1] is the primary diagnostic code
          topline[2] is the list of secondary diagnostic code, 
          topline[3] is the Czech description of the primary code,
          topline[4] is a list of Czech descriptions for the secondary codes
          topline[5] is the origin of the report, always 'brno' for brno data
          topline[6] is the first line of the report, a hospital header

"""
import itertools  as it

topline = idno = None
#path = '../data_clean/brno.tsv'
# 
# when using default, use only training data 
path = '/home/staylor/fall21/ICZ/project_icz/data/brno-train.tsv' 

def linegen(path):
    global topline,idno
    with open(path) as fi:
        topline = None
        idno = -2
        for i,lin in enumerate(fi):
            line = lin.strip().split('\t')
            if i == 0: 
                #print (line)
                continue # skip first row.
            elif len(line) == 1:
                yield line[0]
            elif len(line) ==  2:
                yield line[0]
                yield line[1]
            elif len(line) == 4:
                yield line[0]
                yield line[1]
                yield line[2]
                yield line[3]
            elif len(line) == 5:
                yield line[0]
                yield line[1]
                yield line[2]
                yield line[3]
                yield line[4]
            elif len(line) == 8:
                idno = line[0]
                topline = line[1:]
                yield line[-1]
            else:
                print("oops", len(line), lin, idno)
                break

def wordgen(path):
    delimiters = wordbreaks = {x for x in '!? \t.,:;%$_&^×°~|/[](){}<>"\'+-*\x14\x0b\x0c\r\n=#&\x60\xa0\\|'}
    digits = {x for x in '0123456789'}
    decimal_separator = ",."
    date_separator = "."
    for line in linegen(path):
        word_state = word_start = 0
        for ix,ch in enumerate(it.chain(line,' ')):
            if word_state == 0:
                word_start = ix
                if ch in wordbreaks:
                    continue
                elif ch in digits:
                    word_state = 2
                else:
                    word_state = 1
            elif word_state == 1:#building non-numeric word
                if ch in wordbreaks or ch in digits:
                    yield line[word_start:ix].lower()
                    word_start = ix
                    if ch in digits:
                        word_state = 2
                    else:
                        word_state = 0

            elif word_state == 2: #building int
                if ch in decimal_separator:
                    word_state = 3
                elif ch not in digits:
                    yield '(int)'
                    word_start = ix
                    if ch in wordbreaks:
                        word_state = 0
                    else:
                        word_state = 1

            elif word_state == 3:
                if ch in date_separator:
                    word_state = 4
                elif ch not in digits:
                    yield '(float)'
                    word_start = ix
                    if ch in wordbreaks:
                        word_state = 0
                    else:
                        word_state = 1

            elif word_state == 4:
                if ch not in digits:
                    yield '(date)'
                    word_start = ix
                    if ch in wordbreaks:
                        word_state = 0
                    else:
                        word_state = 1
