# README

# ASPire GPS plotting script
###### Author : Joshua Bruylant
###### Last modified : 04 July 2018
###### Version 1.3

## Setup

1. You may have to install the pathlib library  

   _Linux_ :

   `pip install pathlib` or use your usual installer

   _Mac OS_ :

   `easy_install pathlib` or use your usual installer
&nbsp;
2. Inside your cloned repo run the following commands : 
   ```
   git submodule init
   git submodule update
   cd gpsPlotting/gmplot
   sudo python setup.py install
   ```
   Once gmplot is installed, navigate to where it was installed
   _Linux_ : 
   `/usr/lib/python3.6/site-packages/gmplot-1.2.0-py3.6.egg/gmplot/` and **Replace the existing "gmplot.py" with the one included in your cloned repo situated at Tools/gpsPlotting/**

**-----------------------**

Once gmplot is installed follow these steps : 

1. Navigate to Tools/logExtraction
2. Execute `python3 logExtraction_1.0.py <Test sail database>` and create a GPS CSV file containing the columns : **t_timestamp, latitude, longitude, satellites_used, rc_on**
3. Execute `python3 waypointsToCSV.py <Test sail database>` to create the current mission CSV file
4. Navigate to Tools/gpsPlotting and execute `python3 gpsPlotting_1.3.py <GPS CSV File> <Current Mission CSV> <Interval between each timestamp marker>`


- Replace `<GPS CSV File>` with the name of your gps csv file created earlier
**N.B.:** This csv file must contain the columns t_timestamp, latitude, longitude, satellites_used and rc_on (Use the other script, *logExtraction* in order to easily create this csv file)

- Replace `<Current Mission CSV File>` with the name of your current mission csv created earlier

- Replace `<Interval between each timestamp marker>` with the amount of points you want to skip between placing each timestamp marker.
**Warning** : The lower the interval, the more clustered the map will be. Having the interval too low has a high chance of making the map crash all together.
An interval value of 0 means no markers will be placed


The script will then plot all points and create a route between them on a google map named ASPire_route.html


## Contact

For any questions / suggestions or general comments please address them to joshua.bruylant@ha.ax
