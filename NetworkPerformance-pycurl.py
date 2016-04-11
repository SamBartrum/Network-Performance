from __future__ import division
import pycurl, time, urllib, sys
from matplotlib import pyplot as plt

class NetworkPerformance(object):

	def __init__(self, geturl, posturl, testurl, logindata, delay = 30):
		self.geturl = geturl
		self.posturl = posturl
		self.testurl = testurl
		self.logindata = logindata
		self.timeData = []
		self.goodput = []
		# Create a Curl object
		self.c = pycurl.Curl()

		# Option to allow for more frequent requests
		self.delay = delay

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

		# Get the csrf token
		csrftoken =  self.c.getinfo(pycurl.INFO_COOKIELIST)[0].split("\t")[-1]

		# # Add the crsftoken to the log in data
		self.logindata['csrfmiddlewaretoken'] = csrftoken

		self.c.setopt(pycurl.URL, self.posturl)
		self.c.setopt(pycurl.POSTFIELDS, urllib.urlencode(self.logindata))

		# Perorm the post request
		self.c.perform()


	# Main method to test network performance
	def testNetwork(self, plot = False):
		
		# Authenticate first
		self.authenticate()
		count = 0
		while True:
	
			try: 
				self.c.setopt(pycurl.URL, testurl)
				self.c.perform()

				# The duration we are interested in is the time taken for the data to be transferred in the response
				# So we take the total time and subtract the pre transfer time
				duration = self.c.getinfo(self.c.TOTAL_TIME) - self.c.getinfo(self.c.PRETRANSFER_TIME)
				self.timeData.append(duration)

				# Get data recieved excluding headers
				dataRecieved = self.c.getinfo(pycurl.SIZE_DOWNLOAD)

				# Convert to bits per second
				self.goodput.append( dataRecieved * 8/ duration)

				count += 1 

				# Output the number of requests made, makes it easier to wait if you know somthing is happening
				print "Number of requests made: " + str(count), "\r",
				sys.stdout.flush()

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
			
			# Wait a duration before performing another request, try-except allows for key interupt during this period
			try:
				time.sleep(self.delay)
			except KeyboardInterrupt:
				break

		# Finally print out the results
		if len(self.timeData) != 0:
			print "\nNumber of requests made: " + str(count) 
			print "Average request time: " + str(self.getRTT()) + " seconds"
			print "Average goodput: " + str(self.getGoodPut()) + " bits/second"
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

