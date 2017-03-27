import os
import sys
import datetime
import traceback
import time
from subprocess import call, PIPE, Popen
from csv import reader


def getInputs():
	programToPoll = raw_input('Program/Process to check (no extension needed)?\n')
	sampleInterval = raw_input('How frequently would you like to sample (in seconds)?\n')
	runDuration = raw_input('How long would you like PerfLogger to run? (in seconds and greater than the sample interval\n')
	argList = [programToPoll, sampleInterval, runDuration]
	return argList

def log(msg):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print now, msg

def setUp(argList):
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
		if isinstance(arg, (int, long)):
			continue
		else:
			log('Argument not valid! Value must be an integer')
			try:
				log('Trying to convert string to int...')
				newArg = int(arg)
				for i in (i for i,x in enumerate(argList) if x == arg):
					argList[i] = newArg
			except Exception:
				log(str(traceback.format_exc()))
				break
	return argList

def checkProgram(prgrm):
	prgrmList = []
	p = Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
	output, err = p.communicate()
	if prgrm.lower() in output.lower():
		log(str(prgrm)+' found as a running process!')
	else:
		log(str(prgrm)+' not found running, exiting program')
		exit()

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
	log('Attempting to stop any existing perfmon logger thaty may already be running')
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
	as the other metrics and just change the type ti int
	"""
	cpu = [i[2] for i in data[1:]]
	for i,x in enumerate(cpu):
		if x == ' ':
			cpu[i] = 0
		else:
			cpu[i] = int(x)
	avgCpu = (sum(cpu)/len(cpu))

	# handles are the same as memory
	handles = [int(i[3]) for i in data[1:]]
	avgHandle = (sum(handles)/len(handles))
	log('Average Memory: '+str(avgMemory))
	log('Average CPU: '+str(avgCpu))
	log('Average Handles: '+str(avgHandle))

def cleanUp(fileList):
	try:
		for file in fileList:
			log('Attempting to cleanup file: '+str(file))
			os.remove(file)
	except Exception:
		log(str(traceback.format_exc()))

if __name__ == '__main__':
	fileList = []
	# argList = [sys.argv[1], sys.argv[2], sys.argv[3]]
	argList = getInputs()
	stopPerfmon()
	checkedArgList = setUp(argList)
	createPerfmon(checkedArgList)
	startPerfmon()
	time.sleep(checkedArgList[2])
	convertIt(fileList)
	averages(fileList)
	cleanUp(fileList)


