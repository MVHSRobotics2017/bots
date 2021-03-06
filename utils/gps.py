# # #
# File: gps.py
# Function: module for handling GPS communications.
# #

#imports
import serial #for serial comms

#global vars
port = "" #set me via .setPort!
baud = 9600
isPortDefined = 0 #Bool
import sys

#Word Enums
class words():
	latLong = "$GPGGA" #lat long data follows
	timeData = "$GPRMC"#fix data in ZULU
	#format: dddMM.MMMM where d = deg, M = minutes

def parseGPS(rawStr):
	"""Figure out gps sentance and send output to correct func"""
	delimStrA = rawStr.split('b\'') #because the serial data begins with a silly "b'"
#	print(delimStrA)
	delimStrB = delimStrA[1].split(',')
	if delimStrB[0] == words.latLong:
		return(formatLatLong(delimStrB))
	elif delimStrB[0] ==words.timeData:
		return(readTime(delimStrB))
	else:
		return([None]*16)
def readTime(delimStr):
	"""gets time from GPRMC"""
	h=0 #init vars before use
	hStr="" #init vars before use
	m=0 #init vars before use
	mStr="" #init vars before use
	s=0 #init vars before use
	sStr="" #init vars before use
	i=0 #itterator
	for char in delimStr[1]:
		if i<=1: #hh
			hStr += char
		elif i<=3 and i>1: #mm
			mStr += char
		elif i<=5 and i>2: #ss
			sStr += char
		i +=1 #most important thing this.
	h=int(hStr) #casting output to int
	m=int(mStr) #casting output to int
	s=int(sStr) #casting output to int
	return([h,m,s])

def formatLatLong(delimStr):
	"""converts GPGGA data to Degrees, Seconds"""
	#init locals
	latDD = 0
	longDD = 0
	latMM = 0
	longMM=0
	tempString = "" #needed for the concat steps
	#parse rawStr into better format
	#delimStr = rawStr.split(',') #splits str over delim into list(str)
	latV = delimStr[2] #raw value
	latD = delimStr[3] #north/south
	longV = delimStr[4]#raw value
	longD = delimStr[5]#West/East
	#now for the ugly bit...
	#print("latv={lv}".format(lv = latV))
	if(len(latV) ==10): #if the first Deg is zero (not outputted)
		tempString = (latV[0])+(latV[1]) #concat the first two bytes
		#print(tempString)
		latDD = int(tempString)
		i=0 #reset iterator
		tempString = "" #reset tempString
		for x in latV: #for each char byte
			if(i>1):
				tempString+=x
			i +=1
		latMM = float(tempString)
	elif(len(latV) == 11): #if we have all the LatDD bytes
		i=0
		for x in xrange(0,2):
			tempString+=x
			i+=1
		#latDD = int(latV[0])*100+int(latV[1])*10+int(latV[2])
		latDD = int(tempString)
	if(len(longV)==10): #possible contingency
		raise NotImplementedError("the contingency has occurred. FIX ME!")
	elif(len(longV)==11): # if we have all the LongDD bytes
		i=0
		tempString = ""
		#longDD
		tempString = longV[0]+longV[1]+longV[2]
		longDD = int(tempString)
		#print(tempString)
		#LongMM
		tempString = ""
		i=0
		for x in longV: #concat the longitudinal minute value into a single string
			if(i>2):
				tempString+=x
			i+=1
		longMM = float(tempString) #and convert to float (because decimals)
	return([latDD,latMM,longDD,longMM])
def init(Port,Baud):
	global isPortDefined
	global baud
	global port
	if(isPortDefined):
		return() # no need to waste CPU time repeating whats been done
	elif(type(Port)==str and not isPortDefined): #sanity check
		port = Port
		#return(port) #redundant but affirmative feedback
	elif(type(Port)!=str):
		raise TypeError("Expected a string!")
	elif(type(Baud)==int and not isPortDefined): #sanity check
		baud = Baud
		print("baud={a},Baud={b}".format(a=baud,b=baud))
	elif(type(Baud)!=int):
		raise TypeError("Expected an Int!")
	else:
		raise ValueError("Something unexpected occurred!")
		#like, really. This should be unreachable
	isPortDefined = 1
	return([port,baud])

def getSerial():
	"""returns serial object for GPS"""
	global port
	global baud
	print("======\n{a},{b}".format(a=port,b=baud))
	if(isPortDefined): #sanity check
		return(serial.Serial(port, baud))
	else:
		raise ValueError("You need to init the gps longitudinal before attempting to get the object!")
def initGeoFence(pts):
	"""Collects pts datapoints to define the geofence"""
	poly = [None] #init poly structure before populatng
	for x in range(0,pts+1):
		print("--------------\nposition bot at next geofence vertex and hit enter to continue...\n--------------")
		sys.stdin.readline()
		retn = parseGPS(str(theGPS.readline()))
#		print("retn = {}".format(retn))
		while (len(retn)!=4): #if we parsed something other than LL data...
			retn = parseGPS(str(theGPS.readline())) #read an additional line
		poly.append((retn[0]*1e2+retn[1],retn[2]*1E2+retn[3]))
	return(poly)
init('/dev/ttyAMA0',9600)
theGPS = getSerial()
#for x in range(1,20):
#	print(parseGPS(str(theGPS.readline())))
print("poly = {}".format(initGeoFence(4)))
