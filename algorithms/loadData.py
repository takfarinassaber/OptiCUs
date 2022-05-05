import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, text
import sys
import itertools
import numpy as np
import queue
try:
    import pygraphviz
    from networkx.drawing.nx_agraph import graphviz_layout, write_dot
except ImportError:
    try:
        import pydot
        from networkx.drawing.nx_pydot import graphviz_layout, write_dot
    except ImportError:
        raise ImportError("This example needs Graphviz and either "
                          "PyGraphviz or pydot")
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from partitioningProblem import *












##########################################BEGIN CREATION OF BORDER GRAPH
#countryBorderingFilename = "land_borders.xlsx"
countryBorderingFilename = "./data/land+maritime_borders-longformat.xlsx"
dfBorderingCountries = pd.read_excel(countryBorderingFilename, sheet_name='Sheet1', keep_default_na=False, na_values=[''])
dfBorderingCountries.dropna(inplace=True)
G = nx.from_pandas_edgelist(dfBorderingCountries, 'country', 'neighbour')
borderingCountryNames=list(G.nodes)


print("Initial Number of Countries", len(borderingCountryNames))
print("Initial Number of Borders ", len(G.edges))

############################ LOAD Export File
exportsFilename = "./data/DOTS_2014-18_matrix.xlsx"
dfExports = pd.read_excel(exportsFilename, sheet_name='Sheet1', keep_default_na=False, na_values=[''])
dfExports.fillna(0, inplace=True)
exportCountryNames=dfExports.country.unique()
#print(exportCountryNames)
dfExports.set_index('country', inplace=True)
#dfBorderingCountries=dfBorderingCountries.dropna()








############################ LOAD GDP File
exportsFilename = "./data/gdp_2014-18.xlsx"
gdp = pd.read_excel(exportsFilename, sheet_name='Sheet1', keep_default_na=False, na_values=[''])
gdp.fillna(0, inplace=True)
gdpCountryNames=gdp.country.unique()
gdpCountryNamesOrigin=gdp.country_orig.unique()
#print(exportCountryNames)
gdp.set_index('country', inplace=True)




############################ LOAD GDP Composition File
gdpCompoFilename = "./data/GDPcomposition_2016.xlsx"
gdpCompo = pd.read_excel(gdpCompoFilename, sheet_name='Sheet1', keep_default_na=False, na_values=[''])
gdpCompo.fillna(0, inplace=True)
gdpCompoCountryNames=gdpCompo.country.unique()
gdpCompoCountryNamesOrigin=gdpCompo.country_orig.unique()
#print(exportCountryNames)
gdpCompo.set_index('country', inplace=True)
###features= [country country_orig    code    agriculture industry    manufacturing   services    sum]

##################################################
### Make sure all countries in border file and export file are the same
###################################################


a = set(borderingCountryNames)
b = set(exportCountryNames)
c = set(gdpCountryNames)
d = set(gdpCompoCountryNames)
# print(sorted(a))
# print(sorted(b))
# print(sorted(c))
BorderingNotInExport = {element for element in a if element not in b}
ExportNotInBordering = {element for element in b if element not in a}

ExportNotInGDP = {element for element in b if element not in c}
GDPNotInExport = {element for element in c if element not in a}


gdpNotInBordering = {element for element in c if element not in a}
BorderingNotInGDP = {element for element in a if element not in c}


gdpCompoNotInGDP = {element for element in d if element not in c}
gdpNotInGDPCompo = {element for element in c if element not in d}

print("BorderingNotInExport",BorderingNotInExport)
print("ExportNotInBordering",ExportNotInBordering)
print("ExportNotInGDP",ExportNotInGDP)
print("GDPNotInExport",GDPNotInExport)
print("gdpNotInBordering",gdpNotInBordering)
print("BorderingNotInGDP",BorderingNotInGDP)
print("gdpCompoNotInGDP",gdpCompoNotInGDP)
print("gdpNotInGDPCompo",gdpNotInGDPCompo)



for nonExistantCountry in list(set(BorderingNotInExport) | set(BorderingNotInGDP)):
    G.remove_node(nonExistantCountry)
    borderingCountryNames.remove(nonExistantCountry)

for nonExistantCountry in list(set(ExportNotInBordering) | set(ExportNotInBordering)):
    exportCountryNames.remove(nonExistantCountry)

for nonExistantCountry in list(set(GDPNotInExport) | set(gdpNotInBordering)):
    gdpCountryNames.remove(nonExistantCountry)

print("Filtered Number of Countries", len(borderingCountryNames))
print("Filtered Number of Borders ", len(G.edges))

##################################################
### Load Reference Regions
###################################################
import xlrd 
loc = ("data/customs_unions.xlsx") 
  
wb = xlrd.open_workbook(loc) 
sheet = wb.sheet_by_index(0) 
  
sheet.cell_value(0, 0) 


referenceRegions=[]
countriesInReferenceRegion = [True for i in borderingCountryNames]

for i in range(1,sheet.nrows):
    tmpRegion = sheet.row_values(i)
    #print(tmpRegion)
    region=[]
    regionID=tmpRegion[0]
    # print(regionID)
    for country in tmpRegion[2:]:
        #print(country)
        if country != '':
            region.append(country)
            countriesInReferenceRegion[borderingCountryNames.index(country)] = False
    referenceRegions.append(region)

# we create regions of size 1 for all countries that are not part of a reference region
for i in range(len(countriesInReferenceRegion)):
    if countriesInReferenceRegion[i]:
        # print(borderingCountryNames[i])
        referenceRegions.append([borderingCountryNames[i]])

# problem = RegionalIntegrationProblem(gdp, gdpCompo, dfExports, G)
# print(problem.calculateAverageIntegrationScore(referenceRegions))
# print(problem.maxDiffPerSectors(referenceRegions))
# sys.exit(1)


#print(referenceRegions)


