from __future__ import division
import pycurl, time, urllib
from matplotlib import pyplot as plt

class NetworkPerformance(object):

	def __init__(self, geturl, posturl, testurl, logindata):
		self.geturl = geturl
		self.posturl = posturl
		self.testurl = testurl
		self.logindata = logindata
		self.timeData = []
		self.goodput = []
		# Create a Curl object
		self.c = pycurl.Curl()

	# Return the average RTT
	def getRTT(self):
		return sum(self.timeData)/len(self.timeData)

	# Return the average goodput
	def getGoodPut(self):
		return sum(self.goodput)/len(self.goodput)	

	# Authentication method
	def authenticate(self):

		# Suppress output to terminal
		self.c.setopt(pycurl.WRITEFUNCTION, lambda x: None)

		# Turn on cookies
		self.c.setopt(pycurl.COOKIEFILE, "")
		self.c.setopt(pycurl.URL, geturl)
		self.c.perform()

		# Hack to get the csrf token
		csrftoken =  self.c.getinfo(pycurl.INFO_COOKIELIST)[0].split("\t")[-1]

		# # Add the crsftoken to the log in data
		self.logindata['csrfmiddlewaretoken'] = csrftoken

		self.c.setopt(pycurl.URL, self.posturl)
		self.c.setopt(pycurl.POSTFIELDS, urllib.urlencode(self.logindata))

		self.c.perform()


	# # Main method to test network performance
	def testNetwork(self, plot = False):
		
		# Authenticate first
		self.authenticate()

		while True:
	
			try: 
				self.c.setopt(pycurl.URL, testurl)
				self.c.perform()

				# Get the time for this request/response
				duration = self.c.getinfo(self.c.TOTAL_TIME)
				self.timeData.append(duration)

				# Get the average upload/download speeds in bytes per second
				uploadSpeed = self.c.getinfo(pycurl.SPEED_UPLOAD)
				downloadSpeed = self.c.getinfo(pycurl.SPEED_DOWNLOAD)

				self.goodput.append( (uploadSpeed + downloadSpeed)  / 2)

			# The program stops if there is a keyboard interuption
			except KeyboardInterrupt:
				break

			# If the connection is dropped
			except Exception, e:

				print "Connection Error: " + str(e)
				
				# We try and authenticate again
				try:
					self.authenticate()
				except:
					print "Authentication error"
					break
			
			# Wait 30s before performing another request, try-except allows for key interupt
			try:
				time.sleep(30)
			except KeyboardInterrupt:
				break

		if len(self.timeData) != 0:
			print "\nAverage request time: " + str(self.getRTT())
			print "Average goodput: " + str(self.getGoodPut())
		else:
			print "\nNo data collected yet"

		if plot:
			self.plotData()

		self.c.close()

	# Optional plotting method to see network performance visually
	def plotData(self):
		
		plt.hist(self.timeData, label='Round time trip duration')
		plt.show()

		plt.hist(self.goodput, label='Bits transferred per second')
		plt.show()


if __name__ == "__main__":


	geturl = 'http://authenticationtest.herokuapp.com/login/'
	posturl = 'https://authenticationtest.herokuapp.com/login/ajax/'
	testurl = 'https://authenticationtest.herokuapp.com/'

	username = 'testuser'
	password = '54321password12345'
	data = {'username': username, 'password':password}

	# Create the instance
	test = NetworkPerformance(geturl, posturl, testurl, data)

	print "Now running. Press ctr + c to quit the program and return the results"

	# Test the network
	temp = test.testNetwork()

