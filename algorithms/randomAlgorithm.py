
import pandas as pd
import matplotlib.pyplot as plt
import sys
import itertools
import numpy as np
import csv

from partitioningProblem import *
from loadData import *

problem = RegionalIntegrationProblem(gdp, gdpCompo, dfExports, G)




outputfolder="./generationsRandom5/"
probability=0.5



non_dominated_rows=[]
for i in range(1,1000001):
    print(i)
    solution=problem.create_solution(probability)
    problem.evaluate(solution)
    solution.objectives[0], "\t", solution.objectives[1]
    
    row1=[float(solution.objectives[0]),float(solution.objectives[1])]
    dominated=False 
    to_remove_from_non_dominated=[]
    for row2 in non_dominated_rows:
        #print(row1, row2)
        if row2[0]<=row1[0] and row2[1]<=row1[1] :
            dominated=True
            break
        elif row1[0]<=row2[0] and row1[1]<=row2[1] and (row1[0]<row2[0] or row1[1]<row2[1]):
            to_remove_from_non_dominated.append(row2)
    if not(dominated):
        for row2 in to_remove_from_non_dominated:
            non_dominated_rows.remove(row2)
        non_dominated_rows.append(row1)
    
    if (i % 1000 == 0):
        f=open(outputfolder+"result_gen"+str(int(i / 1000))+".tsv", "w")
        for ndrow in non_dominated_rows:
            f.write(str(ndrow[0])+"\t"+str(ndrow[1])+"\n")
        f.close()

