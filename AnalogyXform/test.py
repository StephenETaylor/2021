#!/usr/bin/env python3
"""
This test program sets up parameters for testing the code in subs1.py
"""
import subs1 as s1

for l in [2]:
    s1.TestDictVer = 1
    s1.NoisyTraining = False
    
    s1.setup(l)
    s1.relations = s1.A1relations  
    for p in range(11):
        s1.Pinned = p*10
        for i in range(10):
            s1.main()
