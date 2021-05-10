#!/usr/bin/env python3
"""
    A program for preparing batch files for building embeddings zip files
    takes up to three ordered parameters  on the command line, each with
    defaults*:
       emb_typ {one of fasttext, w2v*, }
       alg_typ {one of cbow, skipgram*
       num repeats {number of different embeddings to build, 10*}
       epochs  {for training.  10*}

    non-parameters:
        always builds 12 embeddings, 25-300
        uses my logon, stephen taylor
        and /storage/plzen1/
        window-size 5

    prepares the following files:
        phjobs.sh  a list of command lines to build separate zip files
                        for different embedding sizes
            these leave files {emb_typ}-{alg_typ}-{size}.zip in
                ~/embeddings-SemEval2020.   Stored file structure:
               data/embeddings/repeat-1/{english-corpus-1, ...}/{embedding file}

        zipup_{emb_typ}-{train-typ}-{repeats}.sh  combines zip files into
         {emb_typ}-{alg_typ}-{repeats}
"""
import sys

def main():
    """ see description above
    """
    emb_typ = 'w2v'
    alg_typ = 'skipgram'
    num_repeats = 10
    epochs = 10
    emb_num = 12

    if len(sys.argv) > 1:
        emb_typ = sys.argv[1]
    if len(sys.argv) > 2:
        alg_typ = sys.argv[2]
    if len(sys.argv) > 3:
        num_repeats = int(sys.argv[3])
    if len(sys.argv) > 4:
        epochs = sys.argv[4]

    window = '5'
    me = 'stephentaylor'
    home = "/bin/bash /storage/plzen1/home/" + me
    lsc = home+"/SemEval2020/task1/python-project/run-lsc_ST.sh"
    emb_name = '-'.join([emb_typ, alg_typ, window, str(epochs)])

    qsub = "qsub -l walltime=18:0:0 -l select=1:ncpus=8:mem=32gb:scratch_local=40gb -j oe -m ae -- "

    #write phjobs.file
    with  open('phjobs.sh', 'w') as fo:
        for k in range(emb_num):
            emb_dim = str((k+1)*25)
            for i in range(num_repeats):

                zip_name = '-'.join([emb_dim, emb_name, str(i)])
                g_f = '-'.join([emb_dim, emb_name])
                params = "--write_zip_file %s.zip --general_folder %s --num_workers 8 --num_repeat 1 --emb_type %s --emb_algorithm %s --emb_dim %s --transformation cca-java --compare_method cosine --use_nearest_neig --iter %s"%(zip_name, g_f, emb_typ, alg_typ, emb_dim, epochs)

                line = ' '.join([qsub, lsc, params])
                print(line, file=fo)

    #now write zipup file
    zips_at = home + '/embeddings-SemEval2020/'
    with  open('zipup-'+emb_name+'.sh', 'w') as fo:
        for k in range(emb_num):
            emb_dim = str((k+1)*25)
            for j in range(num_repeats):
                i = num_repeats - j

                zip_name = '-'.join([emb_dim, emb_name, str(i)])
                fin_zip = '-'.join([emb_dim, emb_name])

                print("unzip", zips_at+zip_name, file=fo)
                print("mv data/embeddings-export/repeat-{1, "+str(i)+"}", file=fo)
            print("zip", fin_zip+'.zip', '-r', 'data/embeddings-export', file=fo)






if __name__ == '__main__':
    main()
