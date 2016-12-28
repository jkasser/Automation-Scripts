from selenium import webdriver
import traceback
import time
import socket

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--incognito")

# driver = webdriver.Chrome(chrome_options=chrome_options)
# driver.implicitly_wait(10)

# def checkIt():
# 	i = 0
# 	try:
# 		i += 1
# 		print 'Attemp #', str(i)
# 		driver.get('https://google.com')
# 		title = driver.title()
# 		if 'google' in title:
# 			print 'Internetz!!!!'
# 		else:
# 			time.sleep(5)
# 			checkIt()
# 	except Exception:
# 		print traceback.format_exc()


# checkIt()


def checkInternet():
	i=0
	for x in range(0,100000):
		try:
			i += 1
			print 'Internet test #', str(i)
			socket.setdefaulttimeout(10)
			host = socket.gethostbyname("www.google.com")
			s = socket.create_connection((host, 80), 2)
			print 'Internet on!'
			return True
		except Exception,e:
			print e
			print 'Internet Off!'
			time.sleep(10)
	return False

checkInternet()