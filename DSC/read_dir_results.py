#!/usr/bin/env python3
"""
    this program reads through the ~/results-SemEval-2020/* files,
    most of which are currently one line by design.

    For each line in the resulting data, the interesting lines are
    selected according to the command-line-switches in column1

    interesting lines have different variables values.
    one variable is the run number, which for all these files is
    the last digit in the zip file name.

    For the maxlinks graph, the independent variables are
     --max_links value      and
     --emb_dim   value

    The dependent variables might be rank correlation: average, or per-language
    which correspond to particular columns in the  line

    for each unique independent variable set,
    average all the dependent variables,
    and output a plot file

"""
import os
import pathline as pl
import sys

EvaluationHeaders = '''Flags	Type	avg acc/rank	w/o Italian acc/rank	english	german	latin	swedish	italian	reverse emb	emb_type	emb_dim	window	iter	use bin thld	use nearest neigh	compare method	k	Type	avg acc/rank	w/o Italian acc/rank	english	german	latin	swedish	italian	reverse emb	emb_type	emb_dim	window	iter	use bin thld	use nearest neigh	compare method	k'''

HeaderTable = EvaluationHeaders.split('\t')
HeaderDict = dict()
for i, x in enumerate(HeaderTable):
    if x in HeaderDict:
        if x+'2' in HeaderDict:
            raise Exception('more than two versions of header '+x)
        else:
            HeaderDict[x+'2'] = i
    else:
        HeaderDict[x] = i

maxlinks_unique = {'emb_typ':'w2v', 'emb_algorithm':'skipgram', 'compare_method':'cosine'}

maxlinks_ind_set = ['emb_dim', 'max_links']

maxlinks_dep_set = {'w/o Italian acc/rank2', 'english2', 'german2', 'latin2', 'swedish2'}

types = {'maxlinks':(maxlinks_unique, maxlinks_ind_set, maxlinks_dep_set)}

this_type = 'maxlinks'
files_dir = '~/results-SemEval-2020/results/'

def main():
    # check commmand line.
        # [Might be pointer to files,
        # name of extraction (i.e.max_links]
    
    # read in files as lines in Table
    Table = []
    for fil in pl.Path(files_dir).iterdir():
        if  fil.is_file():
            with open(fil) as fi:
                for lin in fi:
                    line = fi.split()
                    Table.append(line)

    unique = types[this_type][0]
    indepe = types[this_type][1]
    depend = types[this_type][2]
    ind_sets = dict()
    # get name of unique subset
    unique_name = ''
    for k in sorted(unique.keys()):
        unique_name += ':' + unique[k]

    # for each line in Table,
    for lineno, line in enumerate(Table):
        # extract flags to args dict
        args = getargs(line[HeaderDict['flags']])

        # select this line if unique matches
        sel = True
        for key in unique:
            if unique[key] != args[key]:
                sel = False
                break
        if not sel: continue  # 
                
        # add add this line to seq of ind_set matches
        ind_key = ''
        for key in indepe:
            ind_key += ':' + args[key]
            items = ind_sets.get(ind_key,None)
            if items is None: items = [] # construct a new list
            items.append(lineno)

    # sort ind_sets
    for iset in sorted(ind_sets.keys()):
        # write the independent and dependent variables to a file 
        #  (name based on           unique set values)
        spiset = iset[1:].split(':')
        with open(this_type+unique_name,'w') as fo:
            # for each unique match in ind_sets
            sums = [0]*(len(dep)+1) #entry for each dep var and count
            for lns in ind_sets[iset]:
                # average the dep variables for all lines in sequence
                line = Table[lns]
                sums[-1] += 1 # this is the count
                for i,k in enumerate(depende):
                    sums[i] += float(line[HeaderDict[k]])
                # write the independent variables
                for val in spiset:
                    print(val,sep='\t',end = '\t', file=fo)
                # write the dependent variables
                for val in sums[:-1]:
                    print(val/sums[-1],sep='\t',end = '\t', file=fo)
                print(file=fo)

def getargs(string):



