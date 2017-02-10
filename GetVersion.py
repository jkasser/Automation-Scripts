import os.path
from datetime import datetime
from subprocess import call
import codecs
import traceback

def getVersion():
	try:
		print str(datetime.now())[:19], 'Getting file version'
		path = os.path.expandvars('C:\\\Program Files\\\ProductFolder\\\Product.exe')
		call('wmic datafile where name=\"'+str(path)+'\" get version > output.txt', shell = True)
		fileLines = []
		with codecs.open('output.txt', 'rb', "utf-16") as f:
			for line in f.readlines():
				fileLines.append(line)
		version=str(fileLines[1]).strip()
		return version
	except:
		print traceback.format_exc()

if __name__ == "__main__":
	version = getVersion()
	# print version