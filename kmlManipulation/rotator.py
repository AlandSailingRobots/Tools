import math as m
import sys
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) > 1:
    filepath = str(sys.argv[1])
else:
    print("USAGE: python rotator.py KMLFile")


eRadius = 6731000
wps = []

#Steps trought tree to find all placemarks
def iterTree(element):
    for child in element:

        if "Point" in child.tag:
            wps.append(parsePoint(child))
        iterTree(child)



#Gets coords and name from placemark
def parsePoint(point):
    lat = ""
    long = ""
    for child in point:
        if "coordinates" in child.tag:
            cord = child.text
            lat = cord.split()[0].split(',')[1]
            long = cord.split()[0].split(',')[0]



    return np.array([float(lat),float(long)])


def latLong2Cartes (cord):

    r = eRadius
    lat = m.radians(float(cord[0]))
    #print ("lat", lat)
    long  = m.radians(float(cord[1]))
    #print("long", long)
    x = r*m.sin(lat)*m.cos(long)
    #print("x" ,x)
    y = r*m.sin(lat)*m.sin(long)
    #print("y", y)
    z = r*m.cos(lat)
    #print("z", z)
    #print ("")
    return np.array([x,y,z])




def cartes2latLong(cord):
    r = eRadius
    x = cord[0]
    y = cord[1]
    z = np.sqrt(np.square(x)+np.square(y))
    lat = m.degrees(m.asin(z/r))
    if x == 0:
        long = 90
    else:
        long = m.degrees(m.atan(y/x))
    return np.array([lat,long])





def getCentroid(cords):
    xSum = 0
    ySum = 0
    for cord in cords:
        xSum = xSum + cord[0]
        ySum = ySum + cord[1]
    Ux = xSum/len(cords)
    Uy = ySum/len(cords)
    return np.array([Ux, Uy])


def rotateCoords (cords, middle, degree):
    rotadedCords = []
    rotRad = m.radians(degree)
    for cord in cords:

        zcord = cord - middle
   #     print("lat ", cord[0], " long ",cord[1] )
        radius = np.sqrt(np.square(zcord[0])+ np.square(zcord[1]))
        if zcord[1] == 0:
            angle = np.pi/2
        elif zcord[1] < 0:
            angle = np.arctan(zcord[0] / zcord[1]) + np.pi
        else:
            angle = np.arctan(zcord[0] / zcord[1])

    #    print("angle ", np.degrees(angle))
        rotLat = radius*np.sin(angle+rotRad)+middle[0]
        rotLong = radius*np.cos(angle+rotRad)+middle[1]
     #   print("rotlat ", rotLat, " rotlong ", rotLong)
        rotadedCords.append(np.array([rotLat,rotLong]))
      #  print("")
    return rotadedCords

def addFolder(root, name = "NONAME"):
    document = list(root)[0]
    startTag = document.tag.replace("Document", "")
    tag = startTag+"Folder"
    folder = ET.SubElement(document, tag)
    folder.text = '\n   '
    folder.tail = '\n'
    tag = startTag+"name"
    nameElement = ET.SubElement(folder, tag)
    nameElement.text = name
    nameElement.tail = '\n  '
    return folder


def addPlacemarkToFolder(folder, nameStr, latLong):
    startTag = folder.tag.replace("Folder", "")
    tag = startTag+"Placemark"
    placemark = ET.SubElement(folder, tag)
    tag = startTag +"name"
    name = ET.SubElement(placemark,tag)
    name.text = nameStr
    tag = startTag + "styleUrl"
    style = ET.SubElement(placemark,tag)
    style.text =   "# icon-1899-0288D1-nodesc"
    tag = startTag +"Point"
    point = ET.SubElement(placemark, tag)
    tag = startTag +"coordinates"
    coords = ET.SubElement(point,tag)
    coords.text = latLong2XmlStr(latLong)

def latLong2XmlStr (latLogn):
    return str(latLogn[1])+","+str(latLogn[0])+",0"


def main():
    np.set_printoptions(suppress=True)
    tree = ET.parse(filepath)
    root = tree.getroot()
    iterTree(root)
    newFolder = addFolder(root)
    print(wps)
    cartWps = []
    for wp in wps:
        cartWps.append(latLong2Cartes(wp))

    U = getCentroid(cartWps)


    plt.close('all')



    fig, axs = plt.subplots()

    UlatLong = cartes2latLong(U)
    print("U latlong ", UlatLong)

    lapNr = 1
    for n in range(20,360, 20):
        lapNr+=1
        rotCords = rotateCoords(wps, UlatLong, n)
        pointNr = 0
        for cord in rotCords:
            pointNr += 1

            axs.plot(cord[1], cord[0], 'ro')
            addPlacemarkToFolder(newFolder,"rot"+str(lapNr)+str(pointNr), cord)

    for i in range(len(cartWps)):

        ucwp = wps[i]# - UlatLong

        axs.plot(ucwp[1], ucwp[0], 'yo')
    axs.plot(UlatLong[1], UlatLong[0], 'bo')
    #axs.plot(0,0,'bo')
    axs.axis('equal')
    plt.show()



    newFile = "rotatedWPS.kml"
    tree.write(newFile, encoding="utf-8", xml_declaration=True,  method="xml")
    file = open(newFile, 'r')
    rawText = file.read()
    file.close()
    rawText = rawText.replace("ns0:", "")
    print(rawText)
    file = open(newFile, 'w')
    file.write(rawText)
    file.close()


main()

