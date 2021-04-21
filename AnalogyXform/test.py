#!/usr/bin/env python3
"""
This test program sets up parameters for testing the code in subs1.py
"""
import subs1 as s1
import sys

if len(sys.argv)>1:
    P = [int(sys.argv[1])]
else: 
    P = [0,  90, 100, 110, 150, 200]

if len(sys.argv)>2:
    R = int(sys.argv[2])
else:
    R = 20

for l in [2]:
    s1.TestDictVer = 1
    s1.NoisyTraining = False
    
    s1.setup(l)
    s1.relations = s1.A2relations  
    for p in P:
        s1.Pinned = p
        for i in range(R):
            s1.main()
