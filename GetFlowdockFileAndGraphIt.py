import requests
import json
import base64
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email import Encoders
from email.Utils import formatdate


baseurl = 'https://api.flowdock.com/'
auth = ''


getNewData = True

def writeToFile(content):
	# Write all the stuff to the file so we can parse it later
	path = os.path.expanduser('~/Desktop/Stats.txt')
	print str(datetime.now())[:19], 'Writing stats to file'
	f = open(os.path.expanduser(path), 'a')
	f.write(content)
	f.close()
	return

def clearFile():
	path = os.path.expanduser('~/Desktop/Stats.txt')
	os.remove(path)

def encodeAuth(auth):
	# B64 encode the auth
	newAuth = base64.b64encode(auth)
	authHeaders = {'Authorization': 'basic '+str(newAuth), 'Accept-Content': 'application/json'}
	return authHeaders

def getEchoStats(authHeaders):
	# This is a message stored as raw string with spaces and its annoying
	print str(datetime.now())[:19], 'Getting new data from thread'
	statList = []
	r = requests.get(baseurl+'flows/stuff/messages', headers = authHeaders)
	# print r.text
	echoResponse = json.loads(r.text)
	# print echoResponse
	for x in echoResponse:
		statList.append(x["content"])
		writeToFile(x["content"])
		# print x["content"]

def parseFile():
	# parse the file, split the string by the : so we can create an embedded list
	path = os.path.expanduser('~/Desktop/Stats.txt')
	variables = []
	print str(datetime.now())[:19], 'Checking stats file'
	f = open(path, 'r+')
	for line in f:
		line = line.split(':')
		variables.append(line)
	f.close()
	# print variables
	return variables

def getKeys(variables):
	# Get the keys which we will use to construct our dictionary
	print str(datetime.now())[:19], 'Parsing variables for key value pairs'
	keys = []
	values = {}
	for x in variables:
		if x[0] not in keys:
			keys.append(x[0])
	newKeys = []
	for key in keys:
		# This is an empty key value pair, remove it
		if key != 'Text':
			newKey = key.rstrip()
			newKeys.append(newKey)
	# print newKeys
	return newKeys

def getValues(variables, newKeys):
	print str(datetime.now())[:19], 'Setting up datasets for matplotlib'
	dataDict = {}
	for x in variables:
		for key in newKeys:
			if key in x[0]:
				# If the key is there just append, if not add it
				if key not in dataDict:
					# Date comes back with the timestamp which we don't care about
					if key == 'Date':
						value = "".join(x[1].split())
						value = value[:10]
						dataDict[str(key)]= [value]
					else:
						value = "".join(x[1].split())
						dataDict[str(key)] = [value]
				else:
					if key == 'Date':
						value = "".join(x[1].split())
						value = value[:10]
						dataDict[key].append(value)
					else:
						value = "".join(x[1].split())
						dataDict[key].append(value)
	# print dataDict		
	return dataDict

def removeFirstEntry(myDict):
	print str(datetime.now())[:19], 'Removing first entry which is a duplicate'
	# Something sucks in my loop and i get the first dataset twice
	for key, value in myDict.iteritems():
		value.pop(0)
	# print myDict
	return myDict

def createCSV(myDict):
	print str(datetime.now())[:19], 'Creating CSV with dataset'
	path = os.path.expanduser('~/Desktop/Data.csv')
	with open(path, 'wb') as csv_file:
		writer = csv.writer(csv_file)
		for key, value in myDict.items():
			writer.writerow([key, value])

def getDates(myDict):
	print str(datetime.now())[:19], 'Formatting dates as date objects'
	points = []
	for key, value in myDict.iteritems():
		if key == 'Date':
			timeStampData = value
			# print timeStampData
			for d in timeStampData:
				date = datetime.strptime(d,'%Y-%m-%d')
				points.append(date)
	# print points
	return points

def getPlotPoints(myDict, points):
	print str(datetime.now())[:19], 'Plotting it all'
	pp = PdfPages(os.path.expanduser('~/desktop/Stats.pdf'))
	totalGraphs = []
	for key, value in myDict.iteritems():
		if key != 'Date':
			fig = plt.figure()
			plt.plot(points, value)
			fig.autofmt_xdate()
			plt.xticks(points, rotation = 45, ha ='right', fontsize=12)
			plt.suptitle(key)
			plt.gcf().subplots_adjust(bottom=0.15)
			plt.grid(True)
			# plt.show()
			pp.savefig()
			plt.clf()
		# print key
		if 'TotalInstalled' in key:
			totalGraphs.append([key, value])
	# print totalGraphs	
	plt.plot(points, totalGraphs[0][1], label = totalGraphs[0][0])
	plt.plot(points, totalGraphs[1][1], label = totalGraphs[1][0])
	fig.autofmt_xdate()
	plt.xticks(points, rotation = 45, ha ='right', fontsize=12)
	plt.suptitle('Totals')
	plt.gcf().subplots_adjust(bottom=0.15)
	plt.legend(loc=5, borderaxespad=0.)
	plt.grid(True)
	pp.savefig()
	pp.close()

def mailFile():
	############
	# REMOVED #
	############
	# SMTP_SERVER INFO
	SMTP_SERVER = 'smtp.gmail.com'
	SMTP_PORT = 587
	# PDF File we eventually output
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = ", ".join(toaddrs)
	msg['Subject'] = "EchoStats "+str(datetime.now())[:10]
	msg['Date'] = formatdate(localtime = True)
	path = os.path.expanduser('~/desktop/EchoStats.pdf')
	ctype, encoding = mimetypes.guess_type(path)
	ctype = 'application/octet-stream'
	maintype, subtype = ctype.split('/', 1)
	with open(path, 'rb') as f:
		part = MIMEBase(maintype, subtype)
		part.set_payload(f.read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
		print str(datetime.now())[:19], 'Attaching:', str(os.path.basename(path))
		msg.attach(part)
	server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(username,password)    
	server.sendmail(fromaddr, toaddrs, msg.as_string())
	server.quit()
	return

if __name__ == "__main__":
	if getNewData:
		clearFile()
		authHeaders = encodeAuth(auth)
		getEchoStats(authHeaders)
	variables = parseFile()
	newKeys = getKeys(variables)
	dataDict = getValues(variables, newKeys)
	dataDict = removeFirstEntry(dataDict)
	createCSV(dataDict)
	points = getDates(dataDict)
	getPlotPoints(dataDict, points)
	mailFile()

