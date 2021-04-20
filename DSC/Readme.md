Notes for an article on Diachronic Semantic Change.

Plan is an analytic article summarizing experimental results for a variety
of variations to the Procrustes strategy.

Parameters to vary:
embedding type: fastext, cbow, skipgram
embedding width: 25-?
embedding window  5
embedding iterations 5
binary-threshold vs nearest neighbor (a parameter for binary task only)
similarity/distance function: cos, arccos, 
k
reverse embedding: true/false
transform type: cca, orthogonal, ...
[binary task/ranking task  both tasks always performed
language:  languages include English, German, Latin, Swedish, Italian
all languages always performed, but there is no gold data for Italian ranking]


a number of experiments have already been carried out.   Here I summarize
the situation.
