#This makefile describes how to make build the report, given a supply of tsv
# files, one for each set of experiments in the Evaluation spreadsheet.
# it doesn't automate extracting the tsv files, and adding a new
# experiment would require changing these lists

datfiles	=\
5k-Results-fasttext-cbow-Bi-Fo-cosine-cca-java.dat \
5k-Results-fasttext-skipgram-Bi-Fo-cosine-cca-java.dat \
5k-Results-fasttext-skipgram-Bi-Re-cosine-cca-java.dat \
Results-fasttext-cbow-Bi-Fo-arcos-cca-java.dat \
Results-fasttext-cbow-Bi-Fo-cosine-cca-java.dat \
Results-fasttext-cbow-Bi-Re-arcos-cca-java.dat \
Results-fasttext-cbow-Bi-Re-cosine-cca-java.dat \
Results-fasttext-cbow-Ne-Fo-arcos-cca-java.dat \
Results-fasttext-cbow-Ne-Fo-cosine-cca-java.dat \
Results-fasttext-cbow-Ne-Re-arcos-cca-java.dat \
Results-fasttext-cbow-Ne-Re-cosine-cca-java.dat \
Results-fasttext-skipgram-Bi-Fo-arcos-cca-java.dat \
Results-fasttext-skipgram-Bi-Fo-cosine-cca-java.dat \
Results-fasttext-skipgram-Bi-Re-arcos-cca-java.dat \
Results-fasttext-skipgram-Bi-Re-cosine-cca-java.dat \
Results-fasttext-skipgram-Ne-Fo-arcos-cca-java.dat \
Results-fasttext-skipgram-Ne-Fo-cosine-cca-java.dat \
Results-fasttext-skipgram-Ne-Re-arcos-cca-java.dat \
Results-fasttext-skipgram-Ne-Re-cosine-cca-java.dat \
Results-w2v-cbow-Bi-Fo-arcos-cca-java.dat \
Results-w2v-cbow-Bi-Fo-cosine-cca-java.dat \
Results-w2v-cbow-Bi-Re-arcos-cca-java.dat \
Results-w2v-cbow-Bi-Re-cosine-cca-java.dat \
Results-w2v-cbow-Ne-Fo-arcos-cca-java.dat \
Results-w2v-cbow-Ne-Fo-cosine-cca-java.dat \
Results-w2v-cbow-Ne-Re-arcos-cca-java.dat \
Results-w2v-cbow-Ne-Re-cosine-cca-java.dat \
Results-w2v-skipgram-Bi-Fo-arcos-cca-java.dat \
Results-w2v-skipgram-Bi-Fo-cosine-cca-java.dat \
Results-w2v-skipgram-Bi-Re-arcos-cca-java.dat \
Results-w2v-skipgram-Bi-Re-cosine-cca-java.dat \
Results-w2v-skipgram-Ne-Fo-arcos-cca-java.dat \
Results-w2v-skipgram-Ne-Fo-cosine-cca-java.dat \
Results-w2v-skipgram-Ne-Re-arcos-cca-java.dat \
Results-w2v-skipgram-Ne-Re-cosine-cca-java.dat

svfiles	= \
5k-Results-fasttext-cbow-near-bin-cosine-cca-java.tsv \
5k-Results-fasttext-skipgram-near-bin-cosine-cca-java.csv \
Results-fasttext-cbow-near-bin-arcos-cca-java.tsv \
Results-fasttext-cbow-near-bin-cosine-cca-java.tsv \
Results-fasttext-skipgram-near-bin-arcos-cca-java.tsv \
Results-fasttext-skipgram-near-bin-cosine-cca-java.tsv \
Results-w2v-cbow-near-bin-arcos-cca-java.tsv \
Results-w2v-cbow-near-bin-cosine-cca-java.tsv \
Results-w2v-skipgram-near-bin-arcos-cca-java.tsv \
Results-w2v-skipgram-near-bin-cosine-cca-java.tsv \


report.htm:	plotfiles.py plotfiles.txt ${datfiles}
	python3 plotfiles.py
	gnuplot make.gnuplots

# chose a representative .dat file instead of checking dates on all

Results-w2v-skipgram-Ne-Re-cosine-cca-java.dat:	../readResults.py
	python3 ../readResults.py *sv #${svfiles}
