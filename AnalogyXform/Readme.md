The experiments in this directory are a followup of those described in:

    Stephen Taylor and Tomáš Brychcín:
    "Is there a linear subspace in which the difference vectors of word analogy 
    pairs are parallel?"  CICLing International Conference on Computational 
    Linguistics and Intelligent Text Processing, La Rochelle, April 2019. 

I downloaded the English.w2v.bin embedding from vectors.NLPL.eu.
This word2vec format binary  was in file 12.zip; the url is:
    http://vectors.nlpl.eu/repository/20/12.zip

The description is:
    Gigword 5th Edition gensim continuous Skipgram no lemmatization

The Arabic text embedding is from the same site.

The url is:
    http://vectors.nlpl.eu/repository/20/31.zip
The description is:
    Arabic CoNLL17 corpus gensim continuous Skipgram lemmatization=False

[so I cite their paper:
Fares, Murhaf; Kutuzov, Andrei; Oepen, Stephan & Velldal, Erik (2017). Word vectors, reuse, and replicability: Towards a community repository of large-text resources, In Jörg Tiedemann (ed.), Proceedings of the 21st Nordic Conference on Computational Linguistics, NoDaLiDa, 22-24 May 2017. Linköping University Electronic Press. ISBN 978-91-7685-601-7
]

I also use a subset 150000 word subset of the Zahran embeddings,
which seem now to have disappeared from sites.Google.com/site/MohaZahran


The English relations files are the Google Analogy test set, 
    https://www.wikidata.org/wiki/Q32127146
slightly rearranged into pairs (from quadruplets.)
Pairs are easier to work with.
I slightly edited the family relation, because the NLPL embedding did not 
include he, she, his, hers.   

The Arabic relations files are described in the paper:
Stephen Taylor and Tomáš Brychcin, The representation of some phrases in Arabic word semantic vector spaces, Open Computer Science, 8(1), 2018, pp. 182-193


