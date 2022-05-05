import random
import pandas as pd
import networkx as nx
import sys
import itertools
import numpy as np
import math

from jmetal.core.problem import BinaryProblem
from jmetal.core.solution import BinarySolution

"""
.. module:: RegionalIntegrationProblem
   :platform: 
   :synopsis: Single Objective 
.. moduleauthor:: Takfarinas Saber 
"""


class RegionalIntegrationProblem(BinaryProblem):
    """ Class representing Knapsack Problem. """

    def __init__(self, gdp, gdpCompo, dfExports, G):
        super(RegionalIntegrationProblem, self).__init__()

        self.graph=G
        self.gdp=gdp
        self.gdpCompo=gdpCompo
        self.dfExports=dfExports
        self.totalExportsPerCountry = self.dfExports.sum(axis=1) #calculate total exports per country
        self.totalImportsPerCountry = self.dfExports.sum(axis=0) #calculate total imports per country
        self.edges = list(G.edges())
        self.number_of_variables = len(G.edges())
        self.countryNames = list(G.nodes)
        self.noCountries = len(list(G.nodes))

        self.obj_directions = [self.MINIMIZE] # we minimize -1*RegionalIntegrationScore
        self.number_of_objectives = 2
        self.number_of_constraints = 0
        self.bestSolution=None
        self.bestObjective=0

    

    def create_solution(self) -> BinarySolution:
        new_solution = BinarySolution(number_of_variables=1,
                                      number_of_objectives=self.number_of_objectives)

        new_solution.variables[0]=[False for _ in range(self.number_of_variables)]
        # False means the edge is kept, True means the edge is removed
        
        indexes=[i for i in range(self.number_of_variables)]
        random.shuffle(indexes)
        noChanges=random.randrange(0, self.number_of_variables+1)
        for i in range(noChanges):
            new_solution.variables[0][indexes[i]]=True
        return new_solution

    def create_solution(self, percentageTrue=0.5) -> BinarySolution:
        new_solution = BinarySolution(number_of_variables=1,
                                      number_of_objectives=self.number_of_objectives)

        new_solution.variables[0]=[False for _ in range(self.number_of_variables)]
        # False means the edge is kept, True means the edge is removed
        
        indexes=[i for i in range(self.number_of_variables)]
        random.shuffle(indexes)
        noChanges=random.randrange(0, int((self.number_of_variables+1)*percentageTrue))
        for i in range(noChanges):
            new_solution.variables[0][indexes[i]]=True
        return new_solution

    def create_solution_Seeded(self,borderSelection) -> BinarySolution:
        new_solution = BinarySolution(number_of_variables=1,
                                      number_of_objectives=self.number_of_objectives)
        new_solution.variables[0]=[i for i in borderSelection]
        # False means the edge is kept, True means the edge is removed
        
        return new_solution    

    def convertSolutionToRegions(self, solution):
        H = self.graph.copy()
        regions=[]
        for index, bits in enumerate(solution.variables[0]):
            # False means the edge is kept, True means the edge is removed
            if bits:
                H.remove_edge(self.edges[index][0],self.edges[index][1])
        connectedComponents = nx.connected_components(H)
        for cc in connectedComponents:
            regions.append(list(cc))
        return regions


    '''
    Start Objective 1
    '''
    def measureDistanceIntegrationSumExportsPlusImports(self, allCountriesInRegion):
        sumExportsInRegion=0.0
        sumImportsInRegion=0.0
        #print("countries:", allCountriesInRegion)
        for countryI in range(len(allCountriesInRegion)-1):
            for countryJ in range(countryI+1,len(allCountriesInRegion)):
                country1=allCountriesInRegion[countryI]
                country2=allCountriesInRegion[countryJ]
                sumExportsInRegion += self.dfExports.loc[country1,country2]
                sumExportsInRegion += self.dfExports.loc[country2,country1]
                sumImportsInRegion += self.dfExports.loc[country2,country1]
                sumImportsInRegion += self.dfExports.loc[country1,country2]
                # print("dfExports.at[",country1,",",country2,"]:", dfExports.at[country1,country2])
                # print("dfExports.at[",country2,",",country1,"]:", dfExports.at[country2,country1])
        totalExportsOfRegion = self.totalExportsPerCountry.loc[allCountriesInRegion].sum(axis=0)
        totalImportsOfRegion = self.totalImportsPerCountry.loc[allCountriesInRegion].sum(axis=0)
        
        # print("totalExportsOfRegion",totalExportsOfRegion)
        integrationDistance=0
        # productGDPInRegion=np.longdouble(1.0)
        productGDPInRegion=1.0
        for countryI in range(len(allCountriesInRegion)):   
            country1=allCountriesInRegion[countryI]
            #productGDPInRegion *= np.longdouble(self.gdp.at[country1,'gdp'])
            #productGDPInRegion *= self.gdp.at[country1,'gdp']
        if totalExportsOfRegion>0 and productGDPInRegion>0: 
            #integrationDistance=(sumExportsInRegion+sumImportsInRegion)/((totalExportsOfRegion+totalImportsOfRegion)*productGDPInRegion)
            integrationDistance=(sumExportsInRegion+sumImportsInRegion)/(totalExportsOfRegion+totalImportsOfRegion)
        else:
            return 0
            # print("integrationDistance",integrationDistance)
        # print("integrationDistance",integrationDistance)
        # otherData=[integrationDistance*productGDPInRegion, productGDPInRegion]
        return -1*integrationDistance

    def calculateAverageIntegrationScore(self,regions):
        scorePerRegion=[]
        for region in regions:
            scorePerRegion.append(self.measureDistanceIntegrationSumExportsPlusImports(region))
        return np.mean(scorePerRegion)

    '''
    Start Objective 2
    '''
    def measureMaxDiffPerSectors(self, allCountriesInRegion):
        sectors=["agriculture", "industry", "manufacturing", "services"]
        maxDiffPerSector=[0 for s in sectors]
        for sector in sectors:
            minSectorGDP=101 # max is 100%
            maxSectorGDP=-1 # min is 0%
            for country1 in allCountriesInRegion:
                if self.gdpCompo.loc[country1,sector] > maxSectorGDP:
                    maxSectorGDP = self.gdpCompo.loc[country1,sector]
                if self.gdpCompo.loc[country1,sector] < minSectorGDP:
                    minSectorGDP = self.gdpCompo.loc[country1,sector]
            maxDiffPerSector.append(maxSectorGDP-minSectorGDP)
        return np.mean(maxDiffPerSector)

    def maxDiffPerSectors(self,regions):
        scorePerRegion=[]
        for region in regions:
            scorePerRegion.append(self.measureMaxDiffPerSectors(region))
        return np.mean(scorePerRegion)

    def evaluate(self, solution: BinarySolution) -> BinarySolution:
        regions = self.convertSolutionToRegions(solution)
        solution.objectives[0] = self.calculateAverageIntegrationScore(regions)
        solution.objectives[1] = self.maxDiffPerSectors(regions)
        # print(solution.objectives[0], "\t", solution.objectives[1], "\t", solution.variables[0])
        return solution

    def getBestObjective(self):
        return self.bestObjective

    def getBestSolution(self):
        self.bestSolution

    def get_name(self):
        return 'RegionalIntegrationProblem'