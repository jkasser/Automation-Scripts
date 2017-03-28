import os
import sys
import datetime
import traceback
import time
from subprocess import call, PIPE, Popen
from csv import reader

def log(msg):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print now, msg, '\n'

def getInputs():
	"""
	We want to use raw inputs here because if we used sys.argv then the inputs can be entered in the wrong order, etc etc
	this really limits the potential for screw ups and allows us to add in some helper text since we arent using a gui
	"""
	checkedPrgrm = getProgram()
	sampleInterval = getSampleInt()
	runDuration = getRunDur()
	argList = [checkedPrgrm, sampleInterval, runDuration]
	return argList

def getProgram():
	prgrmToCheck = raw_input('Program/Process to check (no extension needed)?\n')
	p = Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
	output, err = p.communicate()
	if prgrmToCheck.lower() in output.lower():
		log(str(prgrmToCheck)+' found as a running process!')
		return prgrmToCheck
	else:
		log(str(prgrmToCheck)+' not found running, try again!')
		sys.stdout.flush()
		return getProgram()

def getSampleInt():
	try:
		sampleInterval = int(raw_input('How frequently would you like to sample (in seconds)?\n'))
		return sampleInterval
	except ValueError:
		log('Must be a valid integer!')
		return getSampleInt()

def getRunDur():
	try:
		runDuration = int(raw_input('How long would you like PerfLogger to run? (in seconds, must be greater than the sample interval)\n'))
		return runDuration
	except ValueError:
		log('Must be a valid integer!')
		return getRunDur()

def checkArgs(argList):
	if len(argList) < 3:
		log('This script requires 3 arguments! Please try again')
		argList = getInputs()
		checkedArgList = checkArgs(argList)
	elif argList[1] >= argList[2]:
		log('Run duration cannot be less than or equal to the sample size!')
		argList = getInputs()
		checkedArgList = checkArgs(argList)
	else:
		checkedArgList = argList
	return checkedArgList

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
	try:
		# read the csv logger
		file = os.path.expandvars('%UserProfile%\\Desktop\\PerfLogger.csv')
		fileList.append(file)
		with open(file, 'r') as f:
			data = list(reader(f))

		# memory list comprehension to convert strings to ints and average
		memory = [int(i[1]) for i in data[1:]]
		# in case we have no datapoints, ive seen it happen so lets bail out gracefully
		if len(memory) == 0:
			log('We have no datapoints to analyze! Must not have been a valid application')
			return
		else:
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
	except Exception:
		"""
		If something goes wrong this happens when there are 0 datapoints, i.e. no memory etc
		we just want to bail out.
		"""
		log('Something went wrong, perhaps no datapoints present, try again!\n'+str(traceback.format_exc()))
		sys.exit(0)

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
	checkedArgList = checkArgs(argList)
	stopPerfmon()
	createPerfmon(checkedArgList)
	startPerfmon()
	time.sleep(checkedArgList[2])
	convertIt(fileList)
	averages(fileList)
	raw_input('\nPress any key to exit!\n')
	cleanUp(fileList)


