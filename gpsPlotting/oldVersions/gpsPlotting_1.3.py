import sys
import csv
import numpy as np
import math as m
from gmplot import gmplot
from pathlib import Path
from datetime import datetime
from datetime import timedelta

"""
ASPire GPS route plotting script
Author : Joshua Bruylant
Last modified : 04 July 2018
Version 1.3


DESCRIPTION : 
Plots ASPire's route on google maps with two different colours depending on the boat's RC Status and teks into accout timeskips
Requires TWO CSV files : 
	- A GPS CSV File containing t_timestamp, latitude, longitude, satellites_used and rc_on
	- A Current Mission File containing waypoint latitude, longitude and radius

SETUP : Download and execute both python scripts in the logExtraction folder in order to obtain desired CSV Files

HOW TO EXECUTE : 
	python gpsPlotting_1.3.py <Path to GPS CSV file> <Path to Current Mission CSV file> <Interval between each timestamp marker>

N.B.: The lower the interval, the more precise but the more clustered the markers are. Too low may make the map crash because of the density
Marker interval of 0 means no markers will be placed
"""


"""
FUNCTION : getArguments
Retrieves, processes and returns all passed parameters as usable variables
IN
OUT
	:gpsCSVFile - str
	:currentMissionCSVFile - str
	:markerInterval - int
"""
def getArguments():

	gpsCSVFile = sys.argv[1]
	currentMissionCSVFile = sys.argv[2]
	try: #Check marker interval is an int
		markerInterval = int(sys.argv[3])
	except ValueError:
		sys.exit('Invalid Marker Interval')

	#Check that CSV files exist
	if not Path(gpsCSVFile).is_file():
		sys.exit("GPS CSV file doesn't exist or can't be found!")
	if not Path(currentMissionCSVFile).is_file():
		sys.exit("Current Mission CSV file doesn't exist or can't be found!")

	if (markerInterval<35):
		print('\nWARNING : Low marker interval may cause overdensity and map crash\n')

	return gpsCSVFile, currentMissionCSVFile, markerInterval

"""
FUNCTION : CSVToLists
Parses both CSV files to create globally used lists containing all necessary information
IN
	:gpsCSV - str
	:currentMissionCSV - str
	:minSatThreshold - int
OUT
	:times - list of str
	:lats - list of float
	:lons - list of float
	:rcStatus - list of int
	:wpLats - list of float
	:wpLons - list of float
	:wpRadii - list of int
"""
def CSVToLists(gpsCSV, currentMissionCSV, minSatThreshold):

	#Process the current GPS CSV
	with open(gpsCSV, 'r') as csvFile:
		
		reader = csv.reader(csvFile)
		firstLine = next(reader) #Extract the header from the rest
		timeCol, latCol, lonCol, satCol, rcCol = getGPSColumnNumbers(firstLine)

		times, lats, lons, rcStatus = [], [], [], []

		for row in reader:
			numberOfSatellites = int(row[satCol])
			if (numberOfSatellites >= minSatThreshold):
				times.append(row[timeCol]) 
				lats.append(float(row[latCol]))
				lons.append(float(row[lonCol]))
				rcStatus.append(float(row[rcCol]))

	#Process the current mission CSV
	with open(currentMissionCSV, 'r') as csvFile:

		reader = csv.reader(csvFile)
		firstLine = next(reader) #Extract the header from the rest
		latCol, lonCol, radiusCol = getCMColumnNumbers(firstLine)

		wpLats, wpLons, wpRadii = [], [], []

		for row in reader:
			wpLats.append(float(row[latCol]))
			wpLons.append(float(row[lonCol]))
			wpRadii.append(float(row[radiusCol]))

	return times, lats, lons, rcStatus, wpLats, wpLons, wpRadii

"""
FUNCTION : getGPSColumnNumbers
Used in CSVToLists() to retrieve column numbers in the GPS CSV
IN
	:firstLine - iterable
OUT
	:timeCol - int
	:latCol - int
	:lonCol - int
	:satCol - int
	:rcCol - int
"""
def getGPSColumnNumbers(firstLine):

	try:
		timeCol = firstLine.index('t_timestamp')
		latCol = firstLine.index('latitude')
		lonCol = firstLine.index('longitude')
		satCol = firstLine.index('satellites_used')
		rcCol = firstLine.index('rc_on')
	except ValueError:
		sys.exit('Wrong columns or column missing in GPS CSV!')

	return timeCol, latCol, lonCol, satCol, rcCol

"""
FUNCTION : getCMColumnNumbers
Used in CSVToLists() to retrieve column numbers in the Current Mission CSV
IN
	:firstLine - iterable
OUT
	:latCol - int
	:lonCol - int
	:radiusCol -int
"""
def getCMColumnNumbers(firstLine):

	try:
		latCol = firstLine.index('latitude')
		lonCol = firstLine.index('longitude')
		radiusCol = firstLine.index('radius')
	except ValueError:
		sys.exit('Wrong columns or column missing in Current Mission CSV!')

	return latCol, lonCol, radiusCol

"""
FUNCTION : createGmap
Creates the gmap object from the gmplot library on which the route and markers are plotted
IN
OUT
	:gmap - gmplot object
"""
def createGmap():

	#Calculate mean latitude and longitude to center map
	meanLat = np.mean(lats)
	meanLong = np.mean(lons)

	# Place map
	zoom = get_zoom(lats, lons)
	gmap = gmplot.GoogleMapPlotter(meanLat, meanLong, zoom)

	return gmap

"""
FUNCTION : plotPath
Goes through all latitudes and longitudes and plots them on the map with a colour corresponding to RC's status of those points
IN
	:gmap - gmplot object
OUT
"""
def plotPath(gmap):
	linkIndexes=[]
	n=0
	while n<len(rcStatus):
		if rcStatus[n]: #RC is ON
			latCoords, longCoords, linkIndexes, n = addSection(n, linkIndexes, True)
			if len(latCoords)>0 and len(longCoords)>0: #Returned lists aren't empty
				gmap.plot(latCoords, longCoords, '#e67e22', edge_width=2, arrow=True)
		
		else : #RC is OFF
			latCoords, longCoords, linkIndexes, n = addSection(n, linkIndexes, False)
			if len(latCoords)>0 and len(longCoords)>0:
				gmap.plot(latCoords, longCoords, '#2980b9', edge_width=2, arrow=True)
	plotLinks(gmap, linkIndexes)

"""
FUNCTION : plotLinks
Called by plotPath() to plot the missing links created by RC switches or timeskips
IN
	:gmap - gmplot object
	:linkIndexes - list of int
OUT
"""
def plotLinks(gmap, linkIndexes):
	latsToLink = []
	lonsToLink = []
	linkIndexes = set(linkIndexes)
	for index in linkIndexes :
		latsToLink = (lats[index], lats[index+1])
		lonsToLink = (lons[index], lons[index+1])
		gmap.plot(latsToLink, lonsToLink, 'yellow', edge_width=2, edge_alpha=0.3, arrow = True)

"""
FUNCTION : addSection
Called by plotPath() to create a list of coordinates to plot. This list will contain only coordinates with either RC ON or OF
IN
	:n - int
	:linkIndexes - list of int
	:status - bool
OUT
	:latsCoords - list of float
	:lonsCoords - list of float
	:linkIndexes - list of int
	:n - int
"""
def addSection (n, linkIndexes, status):
	latsCoords=[]
	lonsCoords=[]
	
	if not status: #RC Off
		while n<len(rcStatus) and not rcStatus[n]:
			if rcStatus[n-1] and n>0 : #Previous iteration was RC ON, keep track of mode switch
				linkIndexes.append(n-1) 
			
			latsCoords.append(lats[n])
			lonsCoords.append(lons[n]) 
			if not maxTimeDeltaReached(n): #No timeskip between now and next point
				n+=1
			else: #Timeskip detected, current point is end of current path, break to start new one
				linkIndexes.append(n)
				n+=1
				break
			
	if status: #RC On
		while n<len(rcStatus) and rcStatus[n]:
			if not rcStatus[n-1] and n>0: #Previous iteration was RC OFF, keep track of mode switch
				linkIndexes.append(n-1) 
			
			latsCoords.append(lats[n])
			lonsCoords.append(lons[n])
			if not maxTimeDeltaReached(n): #No timeskip between now and next point
				n+=1
			else: #Timeskip detected, current point is end of current path, break to start new one
				linkIndexes.append(n)
				n+=1
				break
		
	return latsCoords, lonsCoords, linkIndexes, n

"""
FUNCTION : maxTimeDeltaReached
Called by addSection() to signal timeskips
IN
	:n - int
OUT
	:maxTimeDeltaReached - bool
"""
def maxTimeDeltaReached(n):
	if n==0 or n>=len(times)-1: 
		return False
	
	#Get times
	currentTime = times[n]
	nextTime = times[n+1]
	
	#Convert them to datetime format
	currentTime = currentTime.split('.')[0] #Remove milliseconds
	nextTime= nextTime.split('.')[0]
	
	currentDatetime = datetime.strptime(currentTime, '%Y-%m-%d_%H:%M:%S')
	nextDatetime = datetime.strptime(nextTime, '%Y-%m-%d_%H:%M:%S')
	
	maxTimeDelta = timedelta(seconds=30) #Threshold at which timeskip is declared
	
	maxTimeDeltaReached = nextDatetime - currentDatetime > maxTimeDelta

	return maxTimeDeltaReached


"""
Functions 'lat_rad' and 'get_zoom' inspired by adamvotava, see https://blog.alookanalytics.com/2017/02/05/how-to-plot-your-own-bikejogging-route-using-python-and-google-maps-api/

Calculates map's zoom based on the latitudes and longitudes
"""
def lat_rad(lat):
	"""
	Helper function for get_zoom()
	"""
	sinus = m.sin(m.radians(lat + m.pi / 180))
	rad_2 = m.log((1 + sinus) / (1 - sinus)) / 2
	return max(min(rad_2, m.pi), -m.pi) / 2
	
def get_zoom(latitudes, longitudes, map_height_pix=900, map_width_pix=1900, zoom_max=21):
	"""
	Algorithm to derive zoom from the activity route. For details please see
	 - https://developers.google.com/maps/documentation/javascript/maptypes#WorldCoordinates
	 - http://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds
	"""

	# at zoom level 0 the entire world can be displayed in an area that is 256 x 256 pixels
	world_heigth_pix = 256
	world_width_pix = 256

	# get boundaries of the activity route
	max_lat = max(latitudes)
	min_lat = min(latitudes)
	max_lon = max(longitudes)
	min_lon = min(longitudes)

	# calculate longitude fraction
	diff_lon = max_lon - min_lon
	if diff_lon < 0:
		fraction_lon = (diff_lon + 360) / 360
	else:
		fraction_lon = diff_lon / 360

	# calculate latitude fraction
	fraction_lat = (lat_rad(max_lat) - lat_rad(min_lat)) / m.pi

	# get zoom for both latitude and longitude
	zoom_lat = m.floor(m.log(map_height_pix / world_heigth_pix / fraction_lat) / m.log(2))
	zoom_lon = m.floor(m.log(map_width_pix / world_width_pix / fraction_lon) / m.log(2))

	return min(zoom_lat, zoom_lon, zoom_max)

"""
FUNCTION : plotMarkers
Plots all desired markers and waypoints with path between them on map
IN
	:gmap - gmplot object
OUT
"""
def plotMarkers(gmap):

	#Place timestamp markers
	if markerInterval :
		for n in range(len(times)):
			if not (n%markerInterval) : #Only place markers every time (n/markerInterval)==0
				gmap.marker(lats[n], lons[n], color = 'lightsalmon', title='{0} \
																			 {1} \
																			 {2}'.format(times[n], lats[n], lons[n]))
				
	#Place waypoint markers
	for row in range(len(wpLats)):
		gmap.marker(wpLats[row], wpLons[row], color = 'crimson', title = 'WAYPOINT {0}\
																			{1}\
																			{2}\
																			{3}'.format(row, wpLats[row], wpLons[row], wpRadii[row]))
		gmap.circle(wpLats[row], wpLons[row], wpRadii[row], color = 'crimson') #Draw radius
	gmap.plot(wpLats, wpLons, color = 'crimson', edge_width=2, closed=True) #Plot path between waypoints


#MAIN SCRIPT
if __name__ == "__main__":

	expectedArgs = 4	

	if (len(sys.argv) == expectedArgs):
		gpsCSV, currentMissionCSV, markerInterval = getArguments()
	else:
		sys.exit("Expected arguments : <GPS CSV> <Current Mission CSV> <Marker interval>")

	minSatThreshold = 5
	times, lats, lons, rcStatus, wpLats, wpLons, wpRadii = CSVToLists(gpsCSV,
																	  currentMissionCSV,
																	  minSatThreshold)
	gmap = createGmap()

	plotPath(gmap)
	plotMarkers(gmap)

	#Draw map
	mapFile = 'mapFile.html'
	gmap.draw(mapFile)
	print("Map creation successful : " + mapFile)

