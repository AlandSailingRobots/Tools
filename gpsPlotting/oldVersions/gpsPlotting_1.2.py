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
Date : 03 July 2018
Version 1.3


Description : 
Extracts latitude and longitude information of ASPire's route and plots them to a google map
Requires a log file containing time, latitude, longitude and satellites_used to be passed as argument when executing the script

HOW TO EXECUTE : python gpsPlotting_1.1.py <Path to csv file> <Interval between each timestamp marker>
N.B.: The lower the interval, the more precise but the more clustered the markers are. Too low may make the map crash because of the density
Marker interval of 0 means no markers will be placed
"""

#28-06-2018 : Added RC on and off differentiation. Orange is RC ON and blue is RC Off
#DONE Account for links between rcon and rcoff, for the moment just creates two separates routes, it should alternate blue/orange 
#29-06 : Getting close to correct links between on and off
#DONE Add waypoint plotting as native feature db -> current_Mission 
#Differences with git version of software : Places waypoints from current_Mission.csv, separates RC ON from RC OFF
#DONE Differentiate separate binaries using the big timeskips in database, each skip = system turned off and turned on again later with new test
#02-07-18 CURRENT STATUS : Takes in same params as before, csv and marker interval but still needs 'current_mission.csv' to be in same location because it uses that too 
#DONE Add dashed lines between status changes and timeskips
#03-07-18 
#TODO Comment new functions, make things clear through light refactoring, add user-friendliness and futureproofing before adding to git, let user input current_mission file, put some try catches in argument reading
#Not possible to have current mission and gps in same csv, same column names
#Find some better way to implement waypoint to csv 


def processArgs():

	expectedArgs = 4	

	if (len(sys.argv) == expectedArgs):
		return getArguments()
	else:
		sys.exit("Expected arguments : <GPS CSV> <Current Mission CSV> <Marker interval>")


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


def CSVToLists(gpsCSV, currentMissionCSV, minSatThreshold):

	with open(gpsCSV, 'r') as csvFile:
		
		reader = csv.reader(csvFile)
		firstLine = next(reader)
		timeCol, latCol, lonCol, satCol, rcCol = getGPSColumnNumbers(firstLine)

		times, lats, lons, rcStatus = [], [], [], []

		for row in reader:
			numberOfSatellites = int(row[satCol])
			if (numberOfSatellites >= minSatThreshold):
				times.append(row[timeCol]) 
				lats.append(float(row[latCol]))
				lons.append(float(row[lonCol]))
				rcStatus.append(float(row[rcCol]))

	with open(currentMissionCSV, 'r') as csvFile:

		reader = csv.reader(csvFile)
		firstLine = next(reader)
		latCol, lonCol, radiusCol = getCMColumnNumbers(firstLine)

		wpLats, wpLons, wpRadii = [], [], [],

		for row in reader:
			wpLats.append(float(row[latCol]))
			wpLons.append(float(row[lonCol]))
			wpRadii.append(float(row[radiusCol]))

	return times, lats, lons, rcStatus, wpLats, wpLons, wpRadii


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

#TODO Add header line to currentMission.csv

def getCMColumnNumbers(firstLine):

	try:
		latCol = firstLine.index('latitude')
		lonCol = firstLine.index('longitude')
		radiusCol = firstLine.index('radius')
	except ValueError:
		sys.exit('Wrong columns or column missing in Current Mission CSV!')

	return latCol, lonCol, radiusCol


def createGmap():

	#Calculate mean latitude and longitude to center map
	meanLat = np.mean(lats)
	meanLong = np.mean(lons)

	# Place map
	zoom = get_zoom(lats, lons)
	gmap = gmplot.GoogleMapPlotter(meanLat, meanLong, zoom)

	return gmap


def plotPath(gmap):
	linkIndexes=[]
	n=0
	while n<len(rcStatus):
		if rcStatus[n]:
			latCoords, longCoords, linkIndexes, n = addSection(n, linkIndexes, True)
			if len(latCoords)>0 and len(longCoords)>0:
				gmap.plot(latCoords, longCoords, '#e67e22', edge_width=2, arrow=True)
		else :
			latCoords, longCoords, linkIndexes, n = addSection(n, linkIndexes, False)
			if len(latCoords)>0 and len(longCoords)>0:
				gmap.plot(latCoords, longCoords, '#2980b9', edge_width=2, arrow=True)
	plotLinks(gmap, linkIndexes)


def plotLinks(gmap, linkIndexes):
	latsToLink = []
	lonsToLink = []
	linkIndexes = set(linkIndexes)
	for index in linkIndexes :
		latsToLink = (lats[index], lats[index+1])
		lonsToLink = (lons[index], lons[index+1])
		gmap.plot(latsToLink, lonsToLink, 'yellow', edge_width=2, edge_alpha=0.3, arrow = True)


def addSection (n, linkIndexes, status):
	latsCoords=[]
	lonsCoords=[]
	
	if not status: #RC Off
		while n<len(rcStatus) and not rcStatus[n]:
			if rcStatus[n-1] and n>0 : linkIndexes.append(n-1) #Previous iteration was RC ON, keep track of mode switch
			#Check for time delta since last point added to list, if it is too great then end append here to end the path and create new one next time
			latsCoords.append(lats[n])
			lonsCoords.append(lons[n])
			if not maxTimeDeltaReached(n) : #No big timeskip detected
				n+=1
			else:
				linkIndexes.append(n)
				n+=1
				break
			
	if status: #RC On
		while n<len(rcStatus) and rcStatus[n]:
			if not rcStatus[n-1] and n>0 : linkIndexes.append(n-1) #Previous iteration was RC OFF, keep track of mode switch
			
			latsCoords.append(lats[n])
			lonsCoords.append(lons[n])
			if not maxTimeDeltaReached(n) : #No big timeskip detected
				n+=1
			else:
				linkIndexes.append(n)
				n+=1
				break
		
	return latsCoords, lonsCoords, linkIndexes, n


def maxTimeDeltaReached(n):
	if n==0 or n>=len(times)-1: 
		return False
	
	#Get times
	currentTime = times[n]
	nextTime = times[n+1]
	
	#Convert them to datetime format
	currentTime = currentTime.split('.')[0]
	nextTime= nextTime.split('.')[0]
	
	currentDatetime = datetime.strptime(currentTime, '%Y-%m-%d_%H:%M:%S')
	nextDatetime = datetime.strptime(nextTime, '%Y-%m-%d_%H:%M:%S')
	
	maxTimeDelta = timedelta(seconds=30) 
	
	maxTimeDeltaReached = nextDatetime - currentDatetime > maxTimeDelta


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
		gmap.circle(wpLats[row], wpLons[row], wpRadii[row], color = 'crimson')
	gmap.plot(wpLats, wpLons, color = 'crimson', edge_width=2, closed=True)


if __name__ == "__main__":

	#get arguments
	#get csv lists
	#get current mission waypoints
	#open map
	#plot path
	#plot waypoints
	#draw map

	gpsCSV, currentMissionCSV, markerInterval = processArgs()

	minSatThreshold = 5
	times, lats, lons, rcStatus, wpLats, wpLons, wpRadii = CSVToLists(gpsCSV,
																	  currentMissionCSV,
																	  minSatThreshold)
	gmap = createGmap()

	plotPath(gmap)
	plotMarkers(gmap)

	mapFile = 'mapFile.html'
	#Draw map
	gmap.draw(mapFile)
	print("Map creation successful : " + mapFile)

