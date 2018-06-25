import sys
import matplotlib.pyplot as plt
import numpy as np
import csv
import math as m
from gmplot import gmplot
from pathlib import Path

"""
ASPire GPS route plotting script
Author : Joshua Bruylant
Date : 25 June 2018
Version 1.0


Description : 
Extracts latitude and longitude information of ASPire's route and plots them to a google map
Requires a log file containing latitude and longitude to be passed as argument when executing the script
"""


#Argument detection and handling
if (len(sys.argv) > 2): #Too many arguments
	sys.exit("Too many arguments! Please give only log file name")
if (len(sys.argv) == 2): #Right amount of arguments, check if file exists
	logFile = sys.argv[1]
	logPathFile = Path(logFile)
	if not logPathFile.is_file():
		sys.exit("Log file doesn't exist or can't be found!")
if (len(sys.argv) < 2): #Not enough arguments
	sys.exit("Please specify log file path!")
		
		 

times=[]
lats=[]
longs=[]

mapFile = 'ASPire_route.html'

#Extract lattitudes and longitudes from logs.csv
with open(logFile, 'r') as csvfile:
	reader = csv.reader(csvfile)
	firstLine = next(reader)
	#Check each header column to determine where the latitudes and longitudes are situated
	for n in range(len(firstLine)):
		if firstLine[n] == 'time' or 't_timestamp' : timeCol = n
			
		if firstLine[n] == 'latitude' : latCol = n 
		else : latCol = False
			
		if firstLine[n] == 'longitude' : longCol = n 
		else : longCol = False
			
		
	
	for row in reader:
		if timeCol : times.append(row[timeCol]) 
		if latCol : lats.append(float(row[latCol])) 
		else : sys.exit("No latitude!")
		if longCol : longs.append(float(row[longCol])) 
		else : sys.exit("No longitude!")

#Calculate mean latitude and longitude to center map
meanLat = np.mean(lats)
meanLong = np.mean(longs)

# Place map
gmap = gmplot.GoogleMapPlotter(meanLat, meanLong, 13)

#Plot route
gmap.plot(lats, longs, 'cornflowerblue', edge_width=5)

#Draw map
gmap.draw(mapFile)

print("Map creation successful : " + mapFile)
