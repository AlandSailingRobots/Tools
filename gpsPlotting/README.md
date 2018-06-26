# README

###### Author : Joshua Bruylant
###### Date : 26 June 2018
###### Version 1.1

## Setup

- In the gmplot folder execute the setup.py install script

_Linux & Mac OS_ : 

```
cd gmplot
sudo python setup.py install
```

- You also have to install the pathlib library

_Linux_ :

`pip install pathlib` or use your usual installer

_Mac OS_ :

`easy_install pathlib` or use your usual installer

**-----**

Once gmplot is installed execute gpsPlotting_1.1 as follows : 

`python gpsPlotting_1.1.py <csv File> <Interval between each timestamp marker>`

- Replace `<csv File>` with the name of your csv file containing latitude and longitude points of ASPire's route
**N.B.:** This csv file must contain the columns time or t_timestamp, latitude, longitude and satellites_used (Use my other script, *logExtraction* in order to easily create this csv file)

- Replace `<Interval between each timestamp marker>` with the amount of points you want to skip between placing each timestamp marker.
**Warning** : The lower the interval, the more clustered the map will be. Having the interval too low (<20 is risky) has a high chance of making the map crash all together.


The script will then plot all points and create a route between them on a google map named ASPire_route.html


## Contact

For any questions / suggestions or general comments please address them to joshua.bruylant@ha.ax
