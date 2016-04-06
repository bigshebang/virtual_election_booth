from flask import Flask, render_template, request, redirect, abort, session, Blueprint
from flask.ext.mysqldb import MySQL
from dateutil.relativedelta import relativedelta
import time, datetime

utils = Blueprint('utils', __name__)

#see if user is currently logged in
def loggedIn():
	return return bool(session.get('id', False))

#get the election_id of the current election
def getCurElection():
	return 0

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
				(data['username'], password))
	result = cur.fetchall()

	if len(result) > 0:
		return True
	else:
		return False
