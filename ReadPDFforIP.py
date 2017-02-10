import PyPDF2
import os
import re

pdfFile = os.path.expanduser('~/Desktop/IP.pdf')
pdfFileObj = open(pdfFile, 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

pageCount = pdfReader.numPages
# print 'Number of pages:', str(pageCount)

ipList = []
for page in range(pageCount):
	# print 'Reading page:', page
	pageObj = pdfReader.getPage(page).extractText()
	# print pageObj
	ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', pageObj)
	# print ip
	if ip:
		ipList.append(ip)

newList = []
for listedIP in ipList:
	for item in listedIP:
		newList.append(item)

print 'Total IPs:', len(newList)
print '|'.join(newList)
