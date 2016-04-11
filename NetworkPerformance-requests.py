from __future__ import division
import requests, time, sys
# Just for optional plotting
from matplotlib import pyplot as plt

# We don't measure the goodput in this script, instead we measure the throughput

class NetworkPerformance(object):

	def __init__(self, geturl, posturl, testurl, logindata, delay = 30):
		self.geturl = geturl
		self.posturl = posturl
		self.testurl = testurl
		self.logindata = logindata
		self.timeData = []
		self.throughput = []

		# Option to allow for more frequent requests
		self.delay = delay

	# Return the average RTT
	def getRTT(self):
		return sum(self.timeData)/len(self.timeData)

	# Return the average goodput
	def getThroughPut(self):
		return sum(self.throughput)/len(self.throughput)	

	# Authentication method
	def authenticate(self):
		# Perform the HTTP get
		r = requests.get(self.geturl)

		# Get the cookie from the response
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
		
		# Little welcome message
		print "Now running. Press ctr + c to quit the program and return the results"

		# Authenticate first
		self.authenticate()
		# Store the number of tests preformed
		count = 0

		while True:
	
			try: 
				# Compute the time between the request and repsonse
				start = time.time()
				r  = requests.get(self.testurl)
				duration = time.time() - start
				self.timeData.append(duration)

				# Get byte size of request and response objects - total data transferred
				responseSize = sys.getsizeof(r)
				requestSize = sys.getsizeof(requests.Request('GET', self.testurl).prepare())
		
				# Convert bytes to bits and compute bits transferred per second
				self.throughput.append( (responseSize + requestSize) * 8 / (duration))

				count += 1

				# Output the number of requests made, makes it easier to wait if you know somthing is happening
				print "Number of requests made: " + str(count), "\r",
				sys.stdout.flush()


			# The program stops if there is a keyboard interuption
			except KeyboardInterrupt:
				break

			# If the connection is dropped
			except requests.exceptions.ConnectionError:

				print "Connection Error"
				
				# We try and authenticate again
				try:
					self.authenticate()
				# If this fails we exit the program
				except:
					print "Authentication error"
					break
			
			# Delay before performing another request, try-except allows for key interupt
			try:
				time.sleep(self.delay)
			except KeyboardInterrupt:
				break

		# Finally print out the results
		if len(self.timeData) != 0:
			print "\n\nNumber of requests made: " + str(count) 
			print "Average round trip time (RTT): " + str(self.getRTT()) + " seconds"
			print "Average goodput: " + str(self.getThroughPut()) + " bits/second"
		else:
			print "\nNo data collected yet"

		# Plot the data if plot = True is passed as an argument in this method
		if plot:
			self.plotData()

	# Simple method to plot the data if wanted
	def plotData(self):
		
		plt.hist(self.timeData, label='Round time trip duration')
		plt.show()

		plt.hist(self.goodput, label='Bits transferred per second')
		plt.show()


if __name__ == "__main__":

	# Set up the urls
	geturl = 'http://authenticationtest.herokuapp.com/login/'
	posturl = 'https://authenticationtest.herokuapp.com/login/ajax/'
	testurl = 'https://authenticationtest.herokuapp.com/'

	# Set up the login data
	username = 'testuser'
	password = '54321password12345'
	data = {'username': username, 'password':password}

	# Create the instance
	test = NetworkPerformance(geturl, posturl, testurl, data)

	# Test the network
	test.testNetwork()







