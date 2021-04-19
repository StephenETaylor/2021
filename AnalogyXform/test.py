#!/usr/bin/env python3
"""
This test program sets up parameters for testing the code in subs1.py
"""
import subs1 as s1

for l in [1,2]:
    s1.setup(l)
    s1.relations = s1.A1relations  
    s1.main()
