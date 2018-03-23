import sys
from datetime import datetime
import traceback
import os

# python teststuff.py Dev Desktop +2 40 True


newEnv = sys.argv[1] 
newPolicy = sys.argv[2]
newRunCount = sys.argv[3]
newReputation = sys.argv[4]
newShouldInstall = sys.argv[5]
updates = [newEnv, newPolicy, newRunCount, newReputation, newShouldInstall]

def editConfig(updates):
	path = os.path.expanduser('~/Desktop/')
	path = 'C:\\EchoPerf\\'
	tempFile = 'tempPerfConfig.py'
	try:
		print str(datetime.now())[:19], 'Renaming config file'
		for filename in os.listdir(path):
			# print filename
			if filename.startswith("perf") and filename.endswith(".py"):
				os.rename(path+filename, path+tempFile)

		print str(datetime.now())[:19], 'Reading old file into new one'
		with open(path+tempFile, 'r') as fold, open(path+'perfConfig.py', 'w') as fnew:
			for line in fold:
				if 'env' in line:
					print str(datetime.now())[:19], 'Writing environment, changing it to:', str(updates[0])
					fnew.write('env = \''+str(updates[0])+'\'\n')
				elif 'policy' in line:
					print str(datetime.now())[:19], 'Writing policy, changing it to:', str(updates[1])
					fnew.write('policy = \''+str(updates[1])+'\'\n')
				elif 'runCount' in line:
					print str(datetime.now())[:19], 'Writing runCount, changing it to:', str(updates[2])
					fnew.write('runCount = \''+str(updates[2])+'\'\n')
				elif 'reputationScore' in line:
					print str(datetime.now())[:19], 'Writing reputationScore, changing it to:', str(updates[3])
					fnew.write('reputationScore = '+str(updates[3])+'\n')
				elif 'shouldInstall' in line:
					print str(datetime.now())[:19], 'Writing shouldInstall, changing it to:', str(updates[4])
					fnew.write('shouldInstall = '+str(updates[4])+'\n')
				else:
					fnew.write(line)
			fold.close()
			fnew.close()
			print str(datetime.now())[:19], 'Config updated! deleting temp file \n'
			os.remove(path+tempFile)
	except:
		print traceback.format_exc()

if __name__ == "__main__":
	editConfig(updates)
