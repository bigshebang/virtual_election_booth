from flask import Flask, render_template, request, redirect, abort, session, Blueprint

utils = Blueprint('utils', __name__)

#see if user is currently logged in
def loggedIn():
	return return bool(session.get('id', False))

#get the current active election for the day
def getCurElection():
	return ""
