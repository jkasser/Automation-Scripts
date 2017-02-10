from subprocess import call
import os
import traceback

def convertIt():
	file = os.path.expanduser('~/Desktop/EchoPerf.blg')
	try:
		call('relog -f csv \"'+file+'\" -o EchoPerf.csv -y')
	except Exception, e:
		print traceback.format_exc()

if __name__ == "__main__":
	convertIt()