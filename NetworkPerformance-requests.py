from __future__ import division
import requests, time, sys
from matplotlib import pyplot as plt

class NetworkPerformance(object):

	def __init__(self, geturl, posturl, testurl, logindata):
		self.geturl = geturl
		self.posturl = posturl
		self.testurl = testurl
		self.logindata = logindata
		self.timeData = []
		self.throughput = []

	# Return the average RTT
	def getRTT(self):
		return sum(self.timeData)/len(self.timeData)

	# Return the average goodput
	def getThroughut(self):
		return sum(self.throughput)/len(self.throughput)	

	# Authentication method
	def authenticate(self):
		r = requests.get(self.geturl)

		cookie = r.cookies
		csrftoken = cookie['csrftoken']

		# Add the crsftoken to the log in data
		self.logindata['csrfmiddlewaretoken'] = csrftoken

		# Post the form data with the cookie to the submissionURL
		r = requests.post(self.posturl, data=self.logindata, cookies=cookie)
 		
 		# Optional access to response data
		return r

	# Main method to test network performance
	def testNetwork(self, plot = False):
		
		# Authenticate first
		self.authenticate()

		while True:
	
			try: 
				start = time.time()
				r  = requests.get(self.testurl)
				duration = time.time() - start
				self.timeData.append(duration)

				# Get byte size of request and response objects
				responseSize = sys.getsizeof(r)
				requestSize = sys.getsizeof(requests.Request('GET', self.testurl).prepare())
		
				# Convert bytes to bits and compute bits transferred per second
				self.throughput.append( (responseSize + requestSize) * 8 / (duration))

			# The program stops if there is a keyboard interuption
			except KeyboardInterrupt:
				break

			# If the connection is dropped
			except requests.exceptions.ConnectionError:

				print "Connection Error"
				
				# We try and authenticate again
				try:
					self.authenticate()
				except:
					print "Authentication error"
					break
			
			# Wait 30s before performing another request, try-except allows for key interupt
			try:
				time.sleep(1)
			except KeyboardInterrupt:
				break

		if len(self.timeData) != 0:
			print "\nAverage request time: " + str(self.getRTT())
			print "Average goodput: " + str(self.getThroughput())
		else:
			print "\nNo data collected yet"

		if plot:
			self.plotData()

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
	temp = test.authenticate()






