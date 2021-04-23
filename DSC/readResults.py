#!/usr/bin/env python3
"""
    read through a results file, one of the pages of the Evaluation spreadsheet,
    saved as a .csv file.
    name of the file NNN-EMB-EMBSUB-near-bin-SIM-XFORM-JAVA
        where NNN is a prefix,
              EMB is one of {fasttext, w2v, ...}
              EMBSUB is one {skipgram, cbow}
              SIM is one of {cos, arccos}
              XFORM is one of {cca}
              JAVA is one of {java}
              presumably SIM, XFORM, JAVA could have different values if
              we collect those statistics

    write 4 files usable as input to gnuplot, with embedding-size the 
    independent variable.
    Each of the 4 covers one of the combinations of 
        ({near,bin},{forward,reverse}) = parms = {Ne-Fo, Ne-Re, Bi-Fo, Bi-Re}
        and is named NNN-EMB-EMBSUB-PARM-XFORM-JAVA.dat
        each line of each dat file includes:
           embeddingSize 7x <binary stats>  7x <rank stats>
              where each of the {binary, rank} stats is two entries,
              a y-value and a y-delta
    Such file can be plotted in gnuplut with (for example)
       plot 'Results-w2v-cbow-Bi-Fo-cca-java.dat' using 1:2:3 with errorbars,\
              '' using 1:16:17 with errorbars
"""
import sys

def main():
    # read names of input files from command line
    fileNameList = sys.argv[1:]
    lnfnl = len(fileNameList)
    if lnfnl == 0:
        print("No files on command line to process")
    else:
        print ('Number of files to process:',lnfnl)

    # process each input file
    for fn in fileNameList:
        print('file:', fn)
        fncomp = fn.split('-')
        if fncomp[1] == 'Results':
            offset = 1
            NNN = fncomp[0]+'-'+fncomp[1]
        else: 
            offset = 0
            NNN = fncomp[0]

        EMB = fncomp[1+offset]
        EMBSUB = fncomp[2+offset]
        near = fncomp[3+offset]
        bin_ = fncomp[4+offset]
        SIM = fncomp[5+offset]
        XFORM = fncomp[6+offset]
        JAVA = fncomp[7+offset]
        delim_ch = ','   # set up a default
        if JAVA[-4:] == '.csv': 
            JAVA = JAVA[:-4]
            delim_ch = ','
        elif JAVA[-4:] == '.tsv': 
            JAVA = JAVA[:-4]
            delim_ch = '\t'

        if near != 'near' or bin_ != 'bin' :
            raise Exception('bad format file name.  near='+near+' bin='+bin_)

        # read in the table
        table = []
        with open(fn) as fi:
            for lin in fi:
                line = split_sv_line(lin,delim_ch,'"')
                table.append(line)
        
        # go through the table and prepare the four output files,
        #   {Ne-Fo, Ne-Re, Bi-Fo, Bi-Re}
        of = [[],[],[],[]]

        columnA = column('A')
        seg = 7
        while seg < len(table):
            # is this actually the beginning of a segment?
            if ( table[seg][columnA] is  None or 
                     type(table[seg][columnA]) is not type('') or
                      'repeat-1' != table[seg][columnA][:8]  ):
                seg += 1
                continue
            # set up params for this segment:
            if table[seg][column('J')] == '0': # REVERSE-EMBEDDING FALSE
                of_set = 0
            else: of_set = 1

            if table[seg][column('O')] == '0':  # USE BIN THLD FALSE
                of_set += 0
            else: of_set += 2

            emb_dim = table[seg][column('L')]

            # find the three summaries lines (may not be exactly ten runs)
            # summaries are all lines without "repeat" at the beginning
            # could instead make sure that params for runs matched...
            while (seg < len(table) and
                    table[seg][columnA] is not None and 
                     type(table[seg][columnA]) is type('') and
                      'repeat' == table[seg][columnA][:6]  ):
                seg += 1

            oline = [ None ] * 29
            oline[0] = emb_dim
            ou = 1
            for p in [column('C'),column('U')]:
                for i in range(7):
                    oline[ou] = table[seg][p+i]    #average
                    ou += 1
                    oline[ou] = table[seg+2][p+i]#confidence range
                    ou += 1
            of[of_set].append(oline)

        # now write out the four files.
        for f in range(4):
            if len(of[f]) == 0: continue
            PARMS = ['Ne-Fo', 'Ne-Re', 'Bi-Fo', 'Bi-Re'][f] 
            fn = '-'.join([NNN,EMB,EMBSUB,PARMS,XFORM,JAVA])+'.dat'
            with open(fn,'w') as fo:
                for line in of[f]:
                    print(' '.join(line),file=fo)



def split_sv_line(lin, delimiter='\t', text_wrap='"'):
    """
        split a delimiter-separated-values line, which may have some fields
        enclosed in the text_wrap character, if they happen to include the
        delimiter character as data.
        I use an FSA instead of simple split, because split can't deal with
        commas/tabs nested inside quotes
    """
    if delimiter == text_wrap:
        raise Exception('delimiter == textwrap')

    while lin[-1] == '\n' or lin[-1] == '\r':
        lin = lin[:-1]  # clear line termination chars for linux, msdos, macos

    state = 0 #beginning of field
    field = None
    line = []
    for ch in lin:
        if state == 0: # beginning of field
            if ch == delimiter:
                line.append(None)
            elif ch == text_wrap:
                field = ''
                state = 1
            else: 
                field = ch
                state = 3

        elif state == 1: #wrapping text
            if ch == text_wrap:
                line.append(field)
                state = 2
            else:
                field += ch

        elif state == 2: #finished wrapping text, insist on delimiter
            if ch == delimiter:
                state = 0
            else:
                raise Exception('non-empty text after matched text_wrap')

        elif state == 3: #building unwrapped field
            if ch == delimiter:
                line.append(field)
                state = 0
            else:
                field += ch

        else: raise Exception('bug')
    # finished with chars in line
    if state == 0: # beginning of field
        return line
    elif state == 1: #wrapping text
        raise Exception('unmatched text-wrapping character')
    elif state == 2: #finished wrapping text, insist on delimiter
        line.append(field)
        # harmless to leave field set for possible debugging
        return line
    elif state == 3: #building unwrapped field
        line.append(field)
        return line





def column(name):
    """
        translate a column name in the spreadsheet into a column in table
    """
    name = name.upper()
    if len(name) == 1:
        left = None
        right = name
    elif len(name) == 2:
        left = name[0]
        right = name[1]
    else:
        raise Exception('bad column name')
    if left is None:
        lval = 0
    else:
        lval = ord(left)+1-ord('A')
    rval = ord(right)-ord('A')

    return 26*lval+rval

    

        





if __name__ == '__main__': main()
