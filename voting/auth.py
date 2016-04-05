from flask import Flask, render_template, request, redirect, abort, session, Blueprint
from flask.ext.mysqldb import MySQL
from flask.ext.hashing import Hashing
import re
from voting.utils import loggedIn, getCurElection

auth = Blueprint('auth', __name__)
db = MySQL()

@auth.route("/register", methods=["GET", "POST"])
def register_page():
	#if user is logged in already, just send them to the home page
	if loggedIn():
		return redirect("/")

	curElection = getCurElection() #get today's election

	if request.method == "GET":
		return render_template("register.html", logged_in=False, show_results=curElection)
	elif request.method == "POST":
		#validate POST data
		error = None
		result = False
		if not validUsername(request.form['username']):
			error = "You must supply a valid username."
		elif not validPass(request.form['password']):
			error = "Password must not be left blank."
		elif request.form['password'] != request.form['password2']:
			error = "Passwords do not match!"
		elif not validFirst(request.form['first']):
			error = "You must supply a valid first name."
		elif not validLast(request.form['last']):
			error = "You must supply a valid last name."
		elif not validBirthday(request.form['birthday']):
			error = "You must supply a valid date of birth."
		elif not validAddress(request.form['address']):
			error = "You must supply a valid address."
		elif not validPhoneNumber(request.form['number']):
			error = "You must supply a valid phone number."
		elif not validParty(request.form['party']):
			error = "You must supply a valid political party."
		elif not validSSN(request.form['ssn']):
			error = "You must supply a valid Social Security Number."
		else:
			result = registerUser(request.form)

		#if successful registration
		if result:
			#setup session and bring em back to the home page
			setupSession(request.form["username"], ssn=request.form["ssn"],
						 first=request.form["first"], last=request.form["last"])
			return redirect("/")
		else: #failed registration
			if not error:
				error = "Registration failed. Please try again."

			return render_template("register.html", error=error, logged_in=False, show_results=curElection)

@auth.route("/", methods=["POST"])
def login():
	#if user is logged in already, just send them to the home page
	if loggedIn():
		return redirect("/")

	curElection = getCurElection() #get today's election

	#validate POST data
	error = None
	result = False
	if not request.form["username"]:
		error = "Username must not be left blank."
	elif not request.form["password"]:
		error = "Password must not be left blank."
	else:
		result = tryLogin(request.form)

	if result: #valid login
		#get and setup various session data
		setupSession(request.form["username"])
		
		return render_template("index.html", logged_in=True, show_results=curElection)
	else: #failed login
		if not error:
			error = "Invalid username/password combination. Try again."

		return render_template("index.html", error=error, logged_in=False, show_results=curElection)

@auth.route("/logout")
def logout():
	#clear session and put em back to the home page
	if loggedIn():
		session.clear()

	return redirect("/")

def registerUser(data):
	#register user and return success or failure
	password = hashPass(data['password'], data['username']) #hash and salt password
	#make data['birthday'] into proper format?

	#get cursor and add user to voters table
	cur = db.connection.cursor()
	cur.execute("INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, " +
				"address, phoneNumber, politicalParty) VALUES ('%s', '%s', '%s', '%s', '%s', " +
				"'%s', '%s', '%s', '%s')", (data['ssn'], data['username'], password,
				data['first'], data['last'], data['birthday'], data['address'], data['number'],
				data['party']))
	result = cur.fetchall()
	
	if len(result) > 0:
		return True
	else:
		return False

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

#hash password with a static salt and dynamic salt of the username
#use sha512 with 1,000,000 rounds for the securities
def hashPass(plainPass, username):
	#hash password through sha512 with 1 million rounds.
	#static salt of 20 random characters, dynamic salt of the username
	staticSalt = "r!6bCZ&2e7a28d6dfE0c"
	shaHasher = Hashing()
	h = shaHasher.hash_value(plainPass, salt=username+staticSalt)
	return h

#get data about the given user and put it into the session data
def setupSession(username, ssn=None, first=None, last=None):
	session.regenerate() #might need to wrap this in a try block

	#put username and other data into session
	session["username"] = username
	if ssn and first and last:
		userData = {}
		userData["id"] = ssn
		userData["first"] = first
		userData["last"] = last
	else:
		userData = getUserData(session["username"])

	session["id"] = userData["id"]
	session["firstname"] = userData["first"]
	session["lastname"] = userData["last"]

#get certain user data and return in a dictionary
def getUserData(username):
	data = {}
	#make some mysql queries so we can get the id/ssn, firstname, lastname.
	return data

#validate an SSN. return True if valid and False if not
#should we do a check to make sure the SSN isn't a duplicate? this way we can tell the user
#otherwise we have no way of really knowing since we won't get a message from the db call
def validSSN(ssn):
	if ssn:
		if re.match("^\d{3}-\d{2}-\d{4}$", ssn): # XXX-XX-XXXX
			return True

	return False

#what is our policy for this? letters, numbers. then one underscore and/or dash?
#also do a database check to make sure the username isn't taken
def validUsername(user):
	if user:
		return True
	else:
		return False

#make policy for min 8 char passwordddddd with at least 1 upper, lower and number
def validPass(password):
	if password:
		return True
	else:
		return False

#make sure first name is valid (letters, dashes, apostrophes)
def validFirst(first):
	if re.match("^[A-Za-z.-']+$", first): # matches upper, lower, whitespace, and dashes 
		return True

	return False

#make sure last name is valid (letters, dashes, apostrophes)
def validLast(last):
	if re.match("^[A-Za-z.-']+$", last): # matches upper, lower, whitespace, and dashes 
		return True

	return False

#make sure the address consists of letters, numbers and spaces
def validAddress(address):
	if address:
		return True
	else:
		return False

#make sure phone number is in the valid XXX-XXX-XXXX format
def validPhoneNumber(number):
	if number:
		if re.match("^\d{3}-\d{3}-\d{4}$", number): # XXX-XXX-XXXX
			return True

	return False

#make sure birthday is valid date that is at least 18 years ago from today
#also validate that it's in YYYY-MM-DD format
def validBirthday(dob):
	if dob:
		#we also need to find some module to verify that the birthday is 
		#18 or more years ago and that it's a valid date in general
		if re.match("^\d{4}-\d{2}-\d{2}$", number): # YYYY-MM-DD
			return True

	return False

#make sure the party isn't blank
#do we need to check for anything else really? I guess it should be numbers, letters and spaces
def validParty(party):
	if party:
		return True
	else:
		return False

