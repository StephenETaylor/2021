The file pg0 is excerpted from SemEval2020/task1/python-project/Run-metacentrum-cca-java-cosine;
it is intended to start a job to produce a score for a single w2v-skipgram-cosine run.  I'm doing one run instead of 10, in hopes it can finish overnight.

I might (write code) to combine several comparisons for each embedding generated, and submit a number of such jobs in parallel.  I'd then need code to combine them 1) for the evaluation spreadsheet; and also (as resplit code) for the .dat
files.
