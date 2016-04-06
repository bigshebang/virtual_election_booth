from flask import Flask, render_template, request, redirect, abort, session, Blueprint
from flask.ext.mysqldb import MySQL

utils = Blueprint('utils', __name__)

#see if user is currently logged in
def loggedIn():
	return return bool(session.get('id', False))

#get the election_id of the current election
def getCurElection():
	return 0

#get the current time in mysql datetime format - YYYY-MM-DD HH:MI:SS
def getCurTime():
	return "2016-04-25 10:00:00"

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
