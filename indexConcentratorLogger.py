#!/usr/bin/env python

# Imports
import signal
import sys
import time
import re
import subprocess
import os.path

# Globalz def
FLAG_CONTINUE = True
theFilename = "./indexConcentratorLogsStats.csv"

# Handles proper exiting
def signal_handler(signal, frame):
	global FLAG_CONTINUE
	FLAG_CONTINUE = False

# Returns current date "YYYY-MM-DD;HH:MM:SS" 
def currentDate():
	return time.strftime("%Y-%m-%d;%H:%M:%S")

# Look for an element's index in a List of Lists
# With a given sub-List's index
def findIndexOfElement(searchIn, subIndex, needle ):
	res = -1
	if  len(searchIn) > 0 :
		for row in range( len( searchIn ) ) :
			if  subIndex < len( searchIn[ row ] ) :
				if  searchIn[ row ][ subIndex ] == needle :
					res = row
					break

	return res


# Save content of a string into a file
# If no filename is given, default format is applied 
def saveStringToFile ( toSave, theFile = '' ):
	if theFile == '' :
		global theFilename
		theFile = theFilename

	open(theFile, 'w').close()
	text_file = open(theFile, "w")
	text_file.write( toSave )
	text_file.close()

# Get lines from file
# Returns a string vector 
def loadStringsFromFile ( filename ):
	with open( filename ) as f:
		lines = f.readlines()
	return lines

# Get lines from string vector
# Return string vectors vector 
def parseSavedStrings ( strings ):
	parsed = []

	# Explode each lines 
	for line in strings :
		partsString = []
		stringParts = re.split(";", line )

		for res in stringParts :
			partsString.append( res )

		parsed.append( partsString )

	return parsed

# Erase doubles in List
def uniquify( seq ):
	set = {}
	map( set.__setitem__, seq, [] )	# /!\ Not order preserving
	return set.keys()

# Get lines from string vector
# Return string vectors vector
def parseRawStrings ( strings ):
	parsed = []

	strings = uniquify( strings )	# Delete doubles
	strings.sort()					# Organize

	# Parsing using Regexes
	for line in strings :
		partsString = []

		regexResults = re.match( '([0-9a-zA-Z\.]+): ([0-9\.]{2,6})% \(([0-9]+)/([0-9]+)\)', line )

		if regexResults:
			for i in range( len( regexResults.groups() ) ) :
				partsString.append( regexResults.group( i ) )

			parsed.append( partsString )

	return parsed

# *********************************************************
# ***********            EXEC SCRIPT            ***********
# *********************************************************

# Execute command and get output
def reloadValues ( script ):
	response = []
	script = script

	try:
		fp = subprocess.check_output( [ script ], stderr=subprocess.STDOUT )
		response =  re.split("\n", fp )	# Explode each lines
										# /!\ To output format!

	except subprocess.CalledProcessError as e:
		out_bytes = e.Output			# Output generated before error
		code      = e.returncode		# Return code

	return response

#**********************************************************
# ************                INIT               ************
# ************              MONOLITH             ************
# **********************************************************
def main ( argv ):
	# Globalz
	global FLAG_CONTINUE	# Looping flag
	global theFilename		# Data filename

	# Localz
	delayMinute = 5			# Default delay between two loops (in minutes)
	maxIter = 1440			# Default max iterations to do
	nIter = 0				# Current iteration
	script = ""				# Script filename (+path) to get raw data

	# Setup and Start
	if len( argv ) > 1 :	# If script arg given (minimum required)
		script = argv[1]

		# Look for extra args
		try:
			if len( argv ) > 2 :
				delayMinute = int( argv[2] )

			if len( argv ) > 3 :
				maxIter = int( argv[3] )

		except ValueError:
			print("Arguments #2 and #3 must be integers")
			FLAG_CONTINUE = False

		# Check if data file exists
		if not os.path.isfile(theFilename):
			try:
				thefile = open(theFilename, 'r+')
				thefile.close()
			except:
				print("File could not be created")
				FLAG_CONTINUE = False

		# Check if script exists
		if not os.path.isfile(script):
			try:
				thefile = open(script, 'r+')
				thefile.close()
			except:
				print("Script cannot be executed")
				FLAG_CONTINUE = False

		# Handles proper exit
		signal.signal(signal.SIGINT, signal_handler)

		# Main loop (flag = True && compteur < max)
		while ( FLAG_CONTINUE and nIter < maxIter ):

			# Get data
			raws = parseRawStrings( reloadValues( script ) );					# Can be replaced with raw file
			parsed = parseSavedStrings( loadStringsFromFile( theFilename ) )	# Get data from data file

			# New data file content
			fullReport = ""

			# For each new line
			for parsedRawOne in raws :
				# Temp vars :
				key = -1			# Index in data file list
				toSave = False		# Has to be saved?
				saveString = ""		# String to save

				# If parsing correct
				if len( parsedRawOne ) == 4 :
					# Looking for the corresponding line in existing data List
					key = findIndexOfElement( parsed, 2, parsedRawOne[ 1 ] )

					# Forge new line to be stored
					saveString = currentDate() + ";" + parsedRawOne[ 1 ] + ";" + parsedRawOne[ 2 ] + ";" + parsedRawOne[ 3 ] + "\n"

					# If line found in data List
					if  key >= 0 and len( parsed[ key ] ) == 5 :
						# Check percentage value
						if float( parsedRawOne[ 2 ] ) <= float( parsed[ key ][ 3 ] ):
							# Keeps the highest
							saveString = parsed[ key ][ 0 ] + ";" + parsed[ key ][ 1 ] + ";" + parsed[ key ][ 2 ] + ";" + parsed[ key ][ 3 ] + ";" + parsed[ key ][ 4 ]

				# Content?
				if len( saveString ) > 0 :
					fullReport = fullReport + saveString		# Store!

			print( currentDate() + " : Mise a jour effectuee." )

			# End of processing :
			saveStringToFile( fullReport )				# Save refreshed data to file
			time.sleep( float( delayMinute * 60 ) )		# Wait <delayMinute> minute(s)
			nIter += 1									# Add one to counter and start again!

		print( "\n>>> It ends now!" )

	# If not, show help line
	else:
		print( "Usage : " + os.path.basename(__file__) + " <path to script> [<refreshing delay (in mins) - default: 5>] [max iterrations - default: 1440 (every mins = 5 days running)]" )

	return 0

main( sys.argv )