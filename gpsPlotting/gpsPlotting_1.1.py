import sys
import csv
import numpy as np
import math as m
from gmplot import gmplot
from pathlib import Path

"""
ASPire GPS route plotting script
Author : Joshua Bruylant
Date : 27 June 2018
Version 1.1


Description : 
Extracts latitude and longitude information of ASPire's route and plots them to a google map
Requires a log file containing time, latitude, longitude and satellites_used to be passed as argument when executing the script

HOW TO EXECUTE : python gpsPlotting_1.1.py <Path to csv file> <Interval between each timestamp marker>
N.B.: The lower the interval, the more precise but the more clustered the markers are. Too low may make the map crash because of the density
Marker interval of 0 means no markers will be placed
"""

expectedArgs = 3

#Argument detection and handling
if (len(sys.argv) > expectedArgs): #Too many arguments
	sys.exit("Too many arguments! Please give following arguments : <csv file name> <Marker interval>")
if (len(sys.argv) == expectedArgs): #Right amount of arguments
	logFile = sys.argv[1] #logFile is first argument
	logPathFile = Path(logFile)
	if not logPathFile.is_file():
		sys.exit("Log file doesn't exist or can't be found!")
	
	markerInterval = int(sys.argv[2])
	if markerInterval>0: #Check if entered value is reasonable
		markerFlag = True #Flag that user wants markers
		#Interval between each marker very low, warn user
		if markerInterval<=35: 
			continueFlag = False
			while not continueFlag :
				check = input("WARNING! Such low interval will result in a very high marker density and things may go wrong! Are you sure? [y/N] : ") or 'no' #defaults to no
				if (check.lower() in ['n', 'no']) :
					continueFlag = 1
					sys.exit("You chose the safe way out")
				elif check.lower() in ['y', 'yes']:
					continueFlag = True
				else : 
					continueFlag = False
	elif markerInterval==0:
		markerFlag = False
	else :
		sys.exit('No negative values possible')
		
if (len(sys.argv) < expectedArgs): #Not enough arguments
	sys.exit("Not enough arguments. Required : <csv file name> <Marker interval>")
		
		 

times=[]	#list containing all timestamps parsed from csv file
lats=[]		#list containing all latitudes
longs=[]	#list of longitudes
sats=[]		#list of all satellites used for each lat/long
minSatellitesThreshold = 6 #Minimum satellites needed in order to trust the data
mapFile = 'ASPire_route.html' #File to write to when drawing map


#Extract lattitudes and longitudes from logs.csv
with open(logFile, 'r') as csvfile:
	reader = csv.reader(csvfile)
	firstLine = next(reader)
	#Check each header column to determine where the latitudes and longitudes are situated
	for n in range(len(firstLine)):
		if (firstLine[n] in ['time', 't_timestamp']) : timeCol = n
			
		if (firstLine[n] == 'latitude') : latCol = n 
			
		if (firstLine[n] == 'longitude') : longCol = n 
		
		if (firstLine[n] == 'satellites_used') : satCol = n 
			
	if not str(latCol) : sys.exit("No Latitude!")	
	if not str(longCol) : sys.exit("No longitude!")
	if not str(satCol) : sys.exit("No satellites_used!")
	if not str(timeCol) : sys.exit("No time!")

	
	#Add values to their list
	for row in reader:
		numberOfSatellites = int(row[satCol])
		if not numberOfSatellites <= minSatellitesThreshold : #Add only points with enough satellites used
			times.append(row[timeCol]) 
			lats.append(float(row[latCol]))
			longs.append(float(row[longCol]))
			#sats.append(int(row[satCol]))

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
	


#Calculate mean latitude and longitude to center map
meanLat = np.mean(lats)
meanLong = np.mean(longs)

# Place map
zoom = get_zoom(lats, longs)
gmap = gmplot.GoogleMapPlotter(meanLat, meanLong, zoom)

#Plot route
gmap.plot(lats, longs, '#2980b9', edge_width=5)

#Place timestamp markers
if markerFlag :
	for n in range(len(times)):
		if not (n%markerInterval) :
			gmap.marker(lats[n], longs[n], color = 'lightsalmon', title='{0} \
																		 {1} \
																		 {2}'.format(times[n], lats[n], longs[n]))

#Draw map
gmap.draw(mapFile)

print("Map creation successful : " + mapFile)
