The experiments in this directory are a followup of those described in:

    Stephen Taylor and Tomáš Brychcín:
    "Is there a linear subspace in which the difference vectors of word analogy 
    pairs are parallel?"  CICLing International Conference on Computational 
    Linguistics and Intelligent Text Processing, La Rochelle, April 2019. 

I downloaded the English.w2v.bin embedding from vectors.NLPL.eu.
This word2vec format binary  was in file 12.zip; the url is:
    http://vectors.nlpl.eu/repository/20/12.zip
The description: 
    Gigword 5th Edition Gensim continuous Skipgram no lemmatization

The English relations files are the Google Analogy test set, 
    https://www.wikidata.org/wiki/Q32127146
slightly rearranged into pairs (from quadruplets.)
Pairs are easier to work with.
I slightly edited the family relation, because the NLPL embedding did not 
include he, she, his, hers.   
