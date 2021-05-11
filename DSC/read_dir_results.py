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
import pathlib as pl
import sys

EvaluationHeaders = ('Flags	Type	avg acc/rank	w/o Italian acc/rank'+
    '\tenglish	german	latin	swedish	italian	reverse emb	emb_type' +
    '\temb_dim	window	iter	use bin thld	use nearest neigh' +
    '\tcompare method	k	Type	avg acc/rank' +
    '\tw/o Italian acc/rank	english	german	latin	swedish	italian' +
    '\treverse emb	emb_type	emb_dim	window	iter	use bin thld' +
    '\tuse nearest neigh	compare method	k')

HeaderTable = EvaluationHeaders.split('\t')
HeaderDict = dict()
for i, x in enumerate(HeaderTable):
    if x in HeaderDict:
        if x+'2' in HeaderDict:
            raise Exception('more than two versions of header '+x)
        HeaderDict[x+'2'] = i
    else:
        HeaderDict[x] = i

Maxlinks_unique = {'emb_type':'w2v', 'emb_algorithm':'skipgram', 'compare_method':'cosine', 'reverse_embedding':'True', 'dont_use_java':'True'}

Maxlinks_ind_set = ['emb_dim', 'max_links']

Maxlinks_dep_set = {'w/o Italian acc/rank2', 'english2', 'german2', 'latin2', 'swedish2'}

types = {'maxlinks':(Maxlinks_unique, Maxlinks_ind_set, Maxlinks_dep_set)}

this_type = 'maxlinks'

Me = "/home/stephentaylor/"
files_dir = Me + 'results-SemEval-2020/results/'

all_lines = False
stats = True

def main():
    """
        combine results files into plotfiles
    """
    # check commmand line.
        # [Might be pointer to files,
        # name of extraction (i.e.max_links]
    global files_dir, all_lines, stats
    state = 0
    for a in sys.argv:
        if state == 0:
            state = 1
        elif state == 1:
            if a == '-all_lines':
                all_lines = True
        elif state == 1:
            if a == '-stats':
                stats = True
        elif state == 1:
            if a == '-nostats':
                stats = False


    # read in files as lines in Table
    Table = []
    for fil in pl.Path(files_dir).iterdir():
        if  fil.is_file():
            with open(fil) as f_in:
                for lin in f_in:
                    line = lin.split('\t')
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
        args = getargs(line[HeaderDict['Flags']])

        # select this line if unique matches
        sel = True
        for key in unique:
            if unique[key] != args[key]:
                sel = False
                break
        if not sel:
            continue  #

        # add add this line to seq of ind_set matches
        ind_key = ''
        for key in indepe:
            val = args[key]
            if val.isdigit(): #number is a positive int.  
                if int(val)>99999999: raise Exception('ugly int')
                val = ('00000000'+val)[-8:]  # introduce leading zeros
            ind_key += ':' + val                   # for lexical sorting
        items = ind_sets.get(ind_key, None)
        if items is None:
            items = [] # construct a new list
        items.append(lineno)
        ind_sets[ind_key] = items

    with open(this_type+unique_name, 'w') as f_out:
    # sort ind_sets
        for iset in sorted(ind_sets.keys()):
        # write the independent and dependent variables to a file
        #  (name based on           unique set values)
            spiset = iset[1:].split(':')
            for i,x in enumerate(spiset):
                spiset[i] = x.lstrip('0') # remove leading zeros...
            # for each unique match in ind_sets
            sums = [0]*(len(depend)+1) #entry for each dep var and count
            for lns in ind_sets[iset]:
                # average the dep variables for all lines in sequence
                line = Table[lns]
                sums[-1] += 1 # this is the count
                if all_lines:
                    # write the independent variables
                    for val in spiset:
                        print(val, sep='\t', end='\t', file=f_out)
                for i, k in enumerate(depend):
                    val = float(line[HeaderDict[k]])
                    sums[i] += val
                    if all_lines:
                        # write the dependent variables
                        print(val, sep='\t', end='\t', file=f_out)
                if all_lines:
                    print(file=f_out)

            if stats:
                # write the independent variables
                for val in spiset:
                    print(val, sep='\t', end='\t', file=f_out)
                # write the dependent variables
                for val in sums[:-1]:
                    print("%.4f"%(val/sums[-1]), sep='\t', end='\t', file=f_out)
                print(sums[-1],file=f_out)

def getargs(string):
    """
        parse the ...:Namespace(...) string from the beginning of a results line
        returning a dict of parameter names and values
    """
    answer = dict()
    argstr = string[1+string.find('('):-1]
    argsar = argstr.split(', ')
    for argp in argsar:
        esign = argp.find('=')
        key = argp[:esign]
        if key[0:1] == '--':
            key = key[2:]
        val = argp[1+esign:]
        if val[0] == "'" or val[0] == '"':
            val = val[1:-1]
        answer[key] = val
    return answer



if __name__ == '__main__':
    main()
