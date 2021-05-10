files = '/storage/plzen1/home/stephentaylor'

qsub = "qsub -l walltime=11:58:0 -l select=1:ncpus=2:mem=12gb:scratch_local=40gb -j oe -m ae  -- "
run = "/bin/bash "
 
lsc = files +"/SemEval2020/task1/python-project/run-lsc_ST.sh"
 
run_lsc = run+lsc 
def base_params() :
    return " --general_folder metacentrum-cca --num_workers 8 --num_repeat 1  --transformation cca-java --compare_method cosine --use_nearest_neig  --reverse_embedding "

def params(zipfile ,emb_dim, emb_type, emb_algorithm, itera):
    temp =  "--read_zip_file %s --emb_type %s --emb_algorithm %s --emb_dim %s --iter %s "
    answ = temp%(zipfile,  'w2v', 'skipgram', str(emb_dim), str(itera))

    return answ + base_params()




           # 300-w2v-skipgram-5-10-0.zip 

# some defaults
emb_type = "w2v"
emb_algorithm = "skipgram"
emb_dim = 300
itera = 10

# the goal of this paricular first run.
max_links_vals = [4000,5000, 7000, 10000, 14000, 19000, 25000, 32000, 40000, 49000, 75000, 100000]

with open('phjobs.sh','w') as fo:
    for ml in max_links_vals:
        mlc = ' --max_links %d '%ml
        zipfile_base = '-'.join([str(emb_dim), emb_type, emb_algorithm,str(5),str(itera)])
        for reps in range(10):
            zip_file = zipfile_base+'-'+str(reps)+'.zip'
            parm = params(zip_file, emb_dim, emb_type, emb_algorithm, itera) + mlc
            com = ' '.join([run_lsc,  parm])
            line = ' '.join([qsub, com]) 
            print(line,file=fo)



        
