from flask import Flask, render_template, request, redirect, abort, session, Blueprint

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
