# Simple python screen scraper for Capital Bikeshare Usage History Data
#
# Scrapes data from the Capital Bikeshare website 
# and returns clean CVS file of Usage History.
#
# Uses mechanize to navigate pages and beautiful soup to extract data.
#
# Re-purposed by Harlan Yu (@harlanyu) for Capital Bikeshare; code originally 
# written by Justin Grimes (@justgrimes) & Josh Tauberer (@joshdata) 
# for scraping WMATA data (https://github.com/justgrimes/WMATA-SmarTrip-Scrapper)

# importing libs
import sys, getopt, re, BeautifulSoup, mechanize

def parse_table(ride_table):

	output = ""
	rows = ride_table.findAll("tr")[1:]
	for row in rows:
		for col in row.findAll("td"):
			output += col.string.strip() + " | "
		output = output[:-3] + "\n"

	return output

def main(argv):

	br = mechanize.Browser()
	br.open("https://www.capitalbikeshare.com/login") #login page
	br.select_form(predicate=lambda f: 'id' in f.attrs and f.attrs['id'] == 'login-form') #form name

	try:
		opts, args = getopt.getopt(argv,"hu:p:",["username=","password="])
	except getopt.GetoptError:
		print 'CABIscraper.py -u <username> -p <password>'
		sys.exit(2)
	if (len(opts) != 2):
		print 'CABIscraper.py -u <username> -p <password>'
		sys.exit(2)

	for opt, arg in opts:
	  if opt == '-h':
	     print 'CABIscraper.py -u <username> -p <password>'
	     sys.exit()
	  elif opt in ("-u", "--username"):
	     br["username"] = arg
	  elif opt in ("-p", "--password"):
	     br["password"] = arg

	# Log-in.

	print "Logging in with username {0} password {1}".format(br["username"],br["password"])
	response1 = br.submit().read()

	print "Parsing response..."
	soup = BeautifulSoup.BeautifulSoup(response1)
	acct_num = soup.find(text="Account Number").findNext("td").string

	print "Downloading data for account number %s..." % acct_num

	# Fetch ride data.

	output = "Trip Number | Start Station | Start Date | End Station | End Date | Duration | Cost | Distance (miles) | Calories Burned | CO2 Offset (lbs.)\n"

	# fetch main Rental History page
	response1 = br.open("https://www.capitalbikeshare.com/member/rentals/")

	while True:

		soup = BeautifulSoup.BeautifulSoup(response1)
		ride_table = soup.find(id="content").findAll("table")[1]

		output += parse_table(ride_table)

		# try to fetch another Rental History page
		try:
			response1 = br.follow_link(text_regex=r">", nr=1).read()
		except:
			break

	filename = "cabi_log_%s.csv" % acct_num
	print "Writing to file '%s'... " % filename,
	output_file = open(filename, "w")
	output_file.write(output)
	output_file.close()
	print "done!"

if __name__ == "__main__":
   main(sys.argv[1:])
