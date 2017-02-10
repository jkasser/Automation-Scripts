import requests
import json
import os
import hashlib
import base64
import uuid
import traceback
import time
import platform
import shutil
from datetime import datetime
from subprocess import call

def getPlatform():
	arch = platform.machine()
	if '86' in arch:
		print str(datetime.now())[:19], 'We are on a 32 bit OS'
		programPath = '%Programfiles%'
	else:
		print str(datetime.now())[:19], 'We are on a 64 bit OS'
		programPath ='%ProgramW6432%'
	return programPath

def clearFile():
	path = os.path.expanduser('~/Desktop/MachineState.txt')
	if os.path.isfile(os.path.expanduser(path)):
		print str(datetime.now())[:19], 'Previous file Found, deleting...'
		os.remove(os.path.expanduser(path))


def getConfigValues():
	variables = []
	print str(datetime.now())[:19], 'Checking Config file for environment variable'
	path = os.path.expanduser('~/Desktop/config.txt')
	f = open(path, 'r+')
	for line in f:
		line = line.split(':')
		variables.append(line)
	f.close()
	return variables

def getVars():
	print str(datetime.now())[:19], 'Setting environment and account variable'
	for var in variables:
		if 'environment' in var[0].lower():
			env = var[1].rstrip()
		elif 'account' in var[0].lower():
			acc = var[1].rstrip()
		elif 'policy' in var[0].lower():
			policy = var[1].rstrip()
	return env, acc, policy


def constructAPI(env, acc): # The two variables we need to create the auth
	############
	# REMOVED #
	############
	m = hashlib.md5() # Call the MD 5 method on new variable M
	m.update(dServicePW) # Update m to MD5 the PW
	eServicePW = str(m.hexdigest()) # Spit out the eoncded PW as a hexdigest

	serviceAuth = base64.b64encode(eServiceUN+':'+eServicePW) # Concatenate the UN/PW with a : and base64 the result
	serviceHeaders = {'Authorization': 'basic '+str(serviceAuth), 'Content-Type': 'application/json', 'Accept': 'application/json'}
	print str(datetime.now())[:19], 'Setting Account Auth:', str(serviceAuth)

	return baseurl, serviceAuth, serviceHeaders

def getPolicyID(baseurl, serviceHeaders, policy):
	print str(datetime.now())[:19], 'Getting policy ID for', str(policy)
	r = requests.get(baseurl+'Endpoint', headers = serviceHeaders)
	policyResponse = json.loads(r.text)
	for x in policyResponse["results"]:
		if x["PolicyName"].lower() == str(policy.lower()):
			polID = x["PolicyID"]
			print str(datetime.now())[:19], 'Policy found! ID is:', str(polID)
			return polID

def installExe(productID, ProductKey, ProductOtherKey, env):
	print str(datetime.now())[:19], 'Installing agent'
	downloadDir = os.path.expanduser('~/Downloads/')
	installParams = 'Product.exe' #Commandline params removed
	call(installParams, cwd = downloadDir, shell=True)
	print str(datetime.now())[:19], 'Agent Installed!'

def downloadFile(env):
	url = 'https://'+str(env)+'.company.com/files/Product.exe'
	r = requests.get(url, stream = True)
	print str(datetime.now())[:19], 'Downloading File'
	with open(os.path.expanduser('~/Downloads/Product.exe'), 'wb') as f:
		f.write(r.content)


def postAgent(baseurl, serviceHeaders, policyID):
	print str(datetime.now())[:19], 'Posting agent to', str(policy), 'policy'
	agentPayload = {
	############
	# REMOVED #
	############
	}
	r = requests.post(baseurl+'Endpoint', data = json.dumps(agentPayload), headers = serviceHeaders)
	postResponse = json.loads(r.text)
	# print postResponse
	productID = postResponse["ProductID"]
	ProductKey = postResponse["ProductKey"]
	ProductOtherKey = postResponse["ProductOtherKey"]
	return productID, ProductKey, ProductOtherKey


def deleteFiles():
	downloadDir = os.path.expanduser('~/Downloads/')
	print str(datetime.now())[:19], 'Checking for any files with Product in the name...'
	for files in os.listdir(downloadDir):
		if "product" in files.lower():
			try:
				print str(datetime.now())[:19], 'Attempting Removal...'
				os.remove(os.path.expanduser(str(downloadDir)+str(files)))
				if not os.path.isfile(files):
					print str(datetime.now())[:19], 'Removal Success!'
			
			except Exception:
				print str(datetime.now())[:19], traceback.format_exc()
	print str(datetime.now())[:19], 'Clean-up of directory complete!'

def checkFile():
	downloadDir = os.path.expanduser('~/Downloads/')
	print str(datetime.now())[:19], 'Checking to see if file finished downloading'
	if os.path.isfile(downloadDir+'Product.exe'):
		print str(datetime.now())[:19], 'Installer download complete'
	else:
		print str(datetime.now())[:19], 'Download not finished, sleeping for 3 seconds'
		time.sleep(3)
		checkFile()

def runUninstall(programPath):
	print str(datetime.now())[:19], 'Attempting to run uninstaller'
	path = os.path.expandvars(programPath+'\\ProductFolder\\unins000.exe /verysilent')
	call(path, shell=False)
	print str(datetime.now())[:19], 'Sleeping for 45 seconds to wait for uninstaller to finish'
	time.sleep(45)
	print str(datetime.now())[:19], 'Checking if all files are gone'
	if os.path.exists(os.path.expandvars(programPath+'\\ProductFolder\\')):
		print str(datetime.now())[:19], 'Files still present, sleeping for 15 more seconds then attempting to delete them...'
		time.sleep(15)
		try:
			shutil.rmtree(os.path.expandvars(programPath+'\\ProductFolder\\'))
			print str(datetime.now())[:19], 'Files deleted!'
		except:
			print str(datetime.now())[:19], traceback.format_exc()

def checkInstalled(programPath):
	print str(datetime.now())[:19], 'Checking if we are installed'
	path = os.path.expandvars(programPath+'\\ProductFolder\\Product.exe')
	if os.path.isfile(path):
		print str(datetime.now())[:19], 'Product Installed already, running uninstaller'
		runUninstall(programPath)
	else:
		print str(datetime.now())[:19], 'Product exe not found! Continuing...'

def checkCapture():
	print str(datetime.now())[:19], 'Checking if capture started'
	path = os.path.expandvars('%ProgramData%\\Logfile.log')
	if os.path.isfile(path):
		log = open(path)
		while 1:
			where = log.tell()
			line = log.readline()
			if not line:
				time.sleep(1)
				log.seek(where)

			else:
				if 'TRACE: Product has started.' in line:
					print str(datetime.now())[:19], 'Product started!'
					log.close()
					return

def createFile(agentID, authToken, env, polID, acc):
	path = "~/desktop/"+'MachineState.txt'
	print str(datetime.now())[:19], 'Writing values file'
	f = open(os.path.expanduser(path), 'w+')
	f.write('AgentID:'+str(agentID)+'\nAuthToken:'+str(authToken)+'\nEnvironment:'+str(env)+'\nPolicyID:'+str(polID)+'\nAccount:'+str(acc)+'\nHostURL:https://'+str(env)+'.company.com/'+'\nInstalled:Done')
	f.close()


# Call it
if __name__ == "__main__":
	programPath = getPlatform()
	clearFile()
	checkInstalled(programPath)
	variables = getConfigValues()
	env, acc, policy = getVars()
	deleteFiles()
	downloadFile(env)
	checkFile()
	baseurl, serviceAuth, serviceHeaders = constructAPI(env, acc)
	polID = getPolicyID(baseurl, serviceHeaders, policy)
	productID, productKey, ProductOtherKey = postAgent(baseurl, serviceHeaders, polID)
	checkFile()
	installExe(productKey, ProductOtherKey, agentID, env)
	checkCapture()
	createFile(productID, serviceAuth, env, polID, acc)

