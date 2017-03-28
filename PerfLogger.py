import os
import sys
import datetime
import traceback
import time
import itertools
from subprocess import call, PIPE, Popen
from csv import reader


def getInputs():
	"""
	We want to use raw inputs here because if we used sys.argv then the inputs can be entered in the wrong order, etc etc
	this really limits the potential for screw ups and allows us to add in some helper text since we arent using a gui
	"""
	programToPoll = raw_input('Program/Process to check? (e.g. Chrome - no extension is needed)\n')
	sampleInterval = raw_input('In seconds, how frequently would you like to sample? (e.g. 1)\n')
	runDuration = raw_input('In Seconds, how long would you like PerfLogger to run? (e.g 60)\n')
	argList = [programToPoll, sampleInterval, runDuration]
	return argList

def log(msg):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print now, msg

def setUp(argList):
	"""
	Again, I don't think we need this, a throwback to when I was passing in args on the command line
	"""
	if len(argList) < 3:
		log('This script requires 3 arguments! Please try again')
		return
	else:
		checkedArgList = checkArgs(argList)

	return checkedArgList

def checkArgs(argList):
	prgrm = argList[0]
	checkProgram(prgrm)
	for arg in argList[1:]:
		"""
		We don't need this bit anymore, its coming in via CMD since we are packaging this as an exe
		therefore the variables will come in as a string and we have help text
		if isinstance(arg, (int, long)):
			continue
		else:
			log('Argument not valid! Value must be an integer')
		"""
		try:
			log('Trying to convert string to int...')
			newArg = int(arg)
			for i in (i for i,x in enumerate(argList) if x == arg):
				argList[i] = newArg
		except Exception:
			log(str(traceback.format_exc()))

	return argList

def checkProgram(prgrm):
	"""
	The ony important check we actually want to do still. We will call tasklist and then pipe the 
	output into a list. Then we can check the tasklist to see if the program entered is there. If the 
	process isn't running then let's bail out because there is no point in continuing. If the process is running
	then we can continue and use this program to pass it into perfmon.
	"""
	prgrmList = []
	p = Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
	output, err = p.communicate()
	if prgrm.lower() in output.lower():
		log(str(prgrm)+' found as a running process!')
	else:
		log(str(prgrm)+' not found running, exiting program')
		sys.exit(0)

def createPerfmon(argList):
	path =  os.path.expandvars('%UserProfile%\\Desktop')
	process = str(argList[0])
	sampleInt = str(argList[1])
	try:
		runTime = str(datetime.timedelta(seconds=argList[2]))
		log('Deleting old counter if it is present')
		call('logman delete PerfLogger')
		log('Creating perfmon counter, log will be created here: '+str(path))
		call('logman create counter PerfLogger -c "\Process('+process+')\Handle Count" "\Process('+process+')\Private Bytes" "\Process('+process+')\% Processor Time" -si '+sampleInt+' -rf '+runTime+' -ow --v -o "'+path+'"\\PerfLogger')
	except:
		print log(str(traceback.format_exc()))

def startPerfmon():
	log('Starting perfmon')
	call('logman.exe start "PerfLogger"', shell=False)

def stopPerfmon():
	log('Attempting to stop any existing perfmon logger that may already be running')
	call('logman.exe stop "PerfLogger"', shell=False)

def convertIt(fileList):
	file = os.path.expandvars('%UserProfile%\\Desktop\\PerfLogger.blg')
	fileList.append(file)
	try:
		path =  os.path.expandvars('%UserProfile%\\Desktop')
		call('relog -f csv \"'+file+'\" -o '+path+'\\PerfLogger.csv -y')
	except Exception, e:
		print traceback.format_exc()

def averages(fileList):
	# read the csv logger
	file = os.path.expandvars('%UserProfile%\\Desktop\\PerfLogger.csv')
	fileList.append(file)
	with open(file, 'r') as f:
		data = list(reader(f))

	# memory list comprehension to convert strings to ints and average
	memory = [int(i[1]) for i in data[1:]]
	avgMemory = (sum(memory)/len(memory))

	"""
	CPU is kind of special
	sometimes perfmon records null values and we have to handle this
	we iterate through the list finding empty strings and replace them with 0
	since the other values are turned as a string we do the same list comprehension
	as the other metrics and just change the type to int
	"""
	cpu = [i[2] for i in data[1:]]
	for i,x in enumerate(cpu):
		if x == ' ':
			cpu[i] = 0
		else:
			cpu[i] = float(x)
	avgCpu = (sum(cpu)/len(cpu))

	# handles are the same as memory
	handles = [int(i[3]) for i in data[1:]]
	avgHandle = (sum(handles)/len(handles))
	# log it all on separate lines
	log('Average Memory: '+str(avgMemory))
	log('Average CPU: '+str(avgCpu))
	log('Average Handles: '+str(avgHandle))
	# call this down here so it's the last thing we do
	detectLeak(memory)

def detectLeak(memory):
	"""
	After many ideas this is what I finally settled on
	Basically if we have more than 5 datapoints of memory consumption then
	we will average out every 5 of them and add those points to a list.
	We can check each average with the consecutive item in the list and see if the average
	is increasing or decreasing, if the average is increasing then there is an indication
	of a memory leak. In order to rule out outliers we want to make sure the trend
	is above a certain amount. So we will subtract 1 from the leak potential if the average
	is less than or equal to the next one in the list, singaling normal fluctuations.
	"""
	leakPotential = 0
	if len(memory) > 5:
		sampleSet = []
		y = 0
		for x in range(1, len(memory)):
			if (x % 5 == 0):
				# print y, x
				sampleSet.append(sum(memory[y:x])/5)
				y = x
		for dp in sampleSet:
			if sampleSet.index(dp) < (len(sampleSet)-1):
				if dp <= sampleSet[sampleSet.index(dp)+1]:
					leakPotential -= 1
				else:
					leakPotential += 1
			else:
				break
		if 3 >= leakPotential >= 1:
			log('Slight possibility of a memory leak found! '+str(leakPotential)+' sampled averages increased more than decreased')
		elif leakPotential > 3:
			log('Good possibility of a memory leak found! '+str(leakPotential)+' sampled averages increased more than decreased')
		elif leakPotential < 1:
			log('No real possibility of a memory leak found! '+str(leakPotential)+' sampled averages increased more than decreased')
	else:
		log('Insufficient data points present! We need more than 5 datapoints to guess if there is a memory leak')


def cleanUp(fileList):
	# Clean up all the files on the desktop
	try:
		for file in fileList:
			log('Attempting to cleanup file: '+str(file))
			os.remove(file)
	except Exception:
		log(str(traceback.format_exc()))

if __name__ == '__main__':
	fileList = []
	argList = getInputs()
	stopPerfmon()
	checkedArgList = setUp(argList)
	createPerfmon(checkedArgList)
	startPerfmon()
	time.sleep(checkedArgList[2])
	convertIt(fileList)
	averages(fileList)
	raw_input('\nPress any key to exit!\n')
	cleanUp(fileList)


