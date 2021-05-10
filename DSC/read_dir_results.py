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
import sys

result_column_headers = ['flags', 

