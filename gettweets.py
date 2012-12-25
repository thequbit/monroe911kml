import sys
import twitter
import _mysql as mysql
import json
import urllib2
from urllib import quote_plus as _q

# a fantastic function borroed from GJ - https://github.com/gregjurman/outages
def get_lat_long(raw):
	query_string = _q(raw)
	uri = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % query_string
	#rint "Updating geo for '%s'" % raw
	
	obj = urllib2.urlopen(uri)
	json_data = json.load(obj)
	try:
		lat_long = json_data['results'][0]['geometry']['location']
	except:
		#rint "    BAD ADDRESS"
		return None, None

	#rint "    $f $f" % (lat_long['lat'], lat_long['lng'])

	return lat_long['lat'], lat_long['lng']

# function borrowed from:
# http://blogs.fluidinfo.com/terry/2009/06/24/python-code-for-retrieving-all-your-tweets/
def fetch(user):
	data = {}
	api = twitter.Api()
	max_id = None
	total = 0
	done = False;
	while done == False:
		statuses = api.GetUserTimeline(user, count=200, max_id=max_id)
		newCount = ignCount = 0
		for s in statuses:
			if s.id in data:
				ignCount += 1
			else:
				data[s.id] = s
				newCount += 1
		total += newCount

		print >>sys.stderr, "Fetched %d/%d/%d new/old/total." % (
			newCount, ignCount, total)

		if newCount == 0:
			break

		# test to see if any of the tweets are from 2011
		for tweet in data.values():
			year = tweet.created_at.split(" ")[5]
			day = tweet.created_at.split(" ")[0]
			if year != "2012":
				print "year 2011 found!"
				# set our done flag since we made it to 2011
				done = True;
				# remove the tweet since it does not belong to 2012
				del data[tweet.id]
				
		max_id = min([s.id for s in statuses]) - 1

	return data.values()

def get_mysql_credentials():
        # read in credentials file
        lines = tuple(open('mysqlcreds.txt', 'r'))

        # return the tuple of the lines in the file
        #
        # host
        # dbname
        # username
        # password
        #
        return lines

# add the tweet to the database.  We only save a small part of the tweet
def add_tweet_to_db(text, lat, lng, date, time):

	# get our db info from our local file
        dbcreds = get_mysql_credentials()

        # decode responce
        host = dbcreds[0].rstrip()
        dbname = dbcreds[1].rstrip()
        username = dbcreds[2].rstrip()
        password = dbcreds[3].rstrip()

        # connect to our database
        database = mysql.connect(host=host,user=username,passwd=password,db=dbname)	

	

# pulls the address out of the tweet text
def decode_address(text):
	#
	# Odor of smoke at 150 VAN AUKER ST , Rochester City
	#

	# split on the at keyword and take the second part
	second = text.split(" at ")[1]
	# split on the ',' and take the first part
	#addr = second.split(" , ")[0]
	
	addr = second

	# return our decoded address
	return addr

# main function
def main(argv):

	#a = "3 Tanglewood Lane, Sandy Hook, CT"
	#print "Looking up '%s'" % a 
	#lat,lng = get_lat_long(a)

	#if lat == None or lng == None:
	#	print "    BAD ADDRESS"
	#else:
	#	print "    %f %f" % (lat, lng)

	print "Fetching all tweets from @monroe911 for the last year ..."

	# get all of the tweets since 2011
	user = "monroe911"
	tweets = fetch(user)

	print "   ... Done!\n"

	print "Pushing those results to the database ..."

	badaddresscnt = 0

	# get our db info from our local file
        dbcreds = get_mysql_credentials()

        # decode responce
        host = dbcreds[0].rstrip()
        dbname = dbcreds[1].rstrip()
        username = dbcreds[2].rstrip()
        password = dbcreds[3].rstrip()

        # connect to our database
        database = mysql.connect(host=host,user=username,passwd=password,db=dbname)

	# iterate through the array of tweets and place the important data into the database
	for tweet in tweets:
		# pull address from tweet
		address = decode_address(tweet.text.encode('utf8'))

		print "Address: %s" % address 		

		# get the lat and long from the address
		lat, lng = latlong = get_lat_long(address)		
		
		if lat == None or lng == None:
			print "    BAD ADDRESS"
			badaddresscnt += 1
	        else:
                	print "    %f %f" % (lat, lng)

			# decode date of tweet
			tweetdate = tweet.created_at.split(" ")[1] + " " + tweet.created_at.split(" ")[2] + " " + tweet.created_at.split(" ")[5]
			# decode time of tweet
			tweettime = tweet.created_at.split(" ")[3]

			# add the tweet to the database with its address lat long info
			#dd_tweet_to_db(tweet.text.encode('utf8'), lat, lng, tweetdate, tweettime)

			# crate query
			query = 'insert into tweets (tweettext,lat,lng,tweetdate,tweettime) values('
			query += '"%s", '% tweet.text.encode('utf8')
			query += "%i, %i, " % (lat,lng)
			query += '"%s", ' % tweetdate
			query += '"%s")' % tweettime

			#print query

			# insert data
			database.query(query)

	print "Reporting $i bad addresses." % badaddresscnt

	print "   ... Done!"

if __name__ == '__main__': sys.exit(main(sys.argv))

