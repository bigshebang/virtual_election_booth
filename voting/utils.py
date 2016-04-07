from flask import Flask, render_template, request, redirect, abort, session, Blueprint
from flask.ext.hashing import Hashing
from flask.ext.mysqldb import MySQL
from dateutil.relativedelta import relativedelta
import time, datetime

utils = Blueprint('utils', __name__)
db = MySQL()

#see if user is currently logged in
def loggedIn():
	return bool(session.get('id', False))

#get the election_id of the current election
def getCurElection():
	timestamp = getDBTimestamp(getCurTime()) #get today in mysql datetime format
	cur = db.connection.cursor()
	cur.execute("SELECT election_id FROM elections WHERE start_date <= %s AND end_date >= %s" +
				"ORDER BY end_date DESC LIMIT 1", [timestamp, timestamp])
	result = cur.fetchall()

	###############################################################################################
	#THIS IS NOT DONE, NEED TO GET THE ID FROM result AND RETURN IT IN THE IF PART
	#the above query should be good though
	###############################################################################################
	# I think it is done now!

	election_ids = []
	for eid in result:
		election_ids.append(eid)

	return election_ids

#get the last election that is no longer accepting votes
def getLastElection():
	timestamp = getDBTimestamp(getCurTime()) #get today in mysql datetime format
	cur = db.connection.cursor()
	cur.execute("SELECT election_id FROM elections WHERE end_date < %s ORDER BY end_date DESC" +
				" LIMIT 1", [timestamp])
	result = cur.fetchall()

	###############################################################################################
	#THIS IS NOT DONE, NEED TO GET THE ID FROM result AND RETURN IT IN THE IF PART
	#the above query should be good though
	###############################################################################################
	# I think it is done now!
	if len(result) != 0:
		return result[0]
	return None

#get the current time in unix timestamp
def getCurTime():
	return time.time()

#get the mysql datetime format (YYYY-MM-DD HH:MI:SS) from a unix timestamp
def getDBTimestamp(timestamp):
	t = time.localtime(timestamp)
	timeStr = "%d-%d-%d %d:%d:%d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
	return timeStr

#convert a mysql datetime format to a unix timestamp
def getUnixTimestamp(timestamp):
	return time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

#see if a given date is 18 or more years ago from today
#http://stackoverflow.com/a/8971809/1200388
def validAge(dob):
	#get datetime object of given dob
	vals = dob.split("-")

	#if date cannot be converted it isn't a real date
	try:
		dobDate = datetime.date(vals[0], vals[1], vals[2])
	except:
		return False

	#get today's date
	today = datetime.date.today()

	#if 18 years or older return true, false if else
	return relativedelta(today, dobDate).years >= 18

#try to login a user given their username and password
def tryLogin(data):
	#hash password
	password = hashPass(data['password'], data['username'])

	#check db if this is a good user/pass combo
	cur = db.connection.cursor()
	cur.execute("SELECT * FROM voters WHERE username = %s AND password = %s",
				[data['username'], password])
	result = cur.fetchall()

	if len(result) > 0:
		return True
	else:
		return False

#hash password with a static salt and dynamic salt of the username
#use sha512 with 1,000,000 rounds for the securities
def hashPass(plainPass, username):
	#hash password through sha512 with 1 million rounds.
	#static salt of 20 random characters, dynamic salt of the username
	staticSalt = "r!6bCZ&2e7a28d6dfE0c"
	shaHasher = Hashing()
	h = shaHasher.hash_value(plainPass, salt=username+staticSalt)
	return h
