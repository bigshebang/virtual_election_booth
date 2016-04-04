from flask import Flask, render_template, request, redirect, abort, session, Blueprint
from flask.ext.mysqldb import MySQL
from flask.ext.hashing import Hashing
import re

auth = Blueprint('auth', __name__)
db = MySQL()

@auth.route("/register", methods=["GET", "POST"])
def register_page():
	#make sure user isn't logged in already before processing registration
	if request.method == "GET":
		return render_template("register.html")
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
		elif not validAddress(request.form['address']): #we should prob separate this into separate fields like city, state, zip
			error = "You must supply a valid address."
		elif not validPhoneNumber(request.form['number']):
			error = "You must supply a valid phone number."
		elif not validParty(request.form['party']):
			error = "You must supply a valid political party."
		elif not validSSN(request.form['ssn']):
			error = "You must supply a valid Social Security Number."
		else:
			result = registerUser(request.form)

		if result:
			return render_template("index.html")
		else:
			if not error:
				error = "Registration failed. Please try again."

			return render_template("register.html", error=error)
	else: #weird HTTP method we don't support -- will we even get here?
		return render_template("index.html")

@auth.route("/", methods=["POST"])
def login():
	#if user is logged in already, just send them to the home page

	#validate POST data
	error = None
	result = False
	if not request.form['username']:
		error = "Username must not be left blank."
	elif not request.form['password']:
		error = "Password must not be left blank."
	else:
		result = tryLogin(request.form)

	if result: #valid login
		session.regenerate()
		#put real values here
		session['username'] = "username"
		session['id'] = "id"
		return render_template("index.html", error="Valid login")
	else: #failed login
		if not error:
			error = "Invalid username/password combination. Try again."

		return render_template("index.html", error=error)

@auth.route("/logout")
def logout():
	#clear session and put em back to the home page
	if loggedIn():
		session.clear()

	return redirect("/")

def registerUser(data):
	#register user and return success or failure
	#make data['password'] into hashed and salted version
	data['password'] = hashPass(data['password'], data['username'])
	#make data['birthday'] into proper format
	#get cursor and add user to voters table
	cur = db.connection.cursor()
	cur.execute("INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, " +
				"address, phoneNumber, politicalParty) VALUES ('%s', '%s', '%s', '%s', '%s', " +
				"'%s', '%s', '%s', '%s')", (data['ssn'], data['username'], data['password'],
				data['first'], data['last'], data['birthday'], data['address'], data['number'],
				data['party']))
	result = cur.fetchall()
	
	if len(result) > 0:
		return True
	else:
		return False

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

def hashPass(plainPass, username):
	#hash password through sha512 with 1 million rounds.
	#static salt of 20 random characters, dynamic salt of the username
	staticSalt = "r!6bCZ&2e7a28d6dfE0c"
	shaHasher = Hashing()
	h = shaHasher.hash_value(plainPass, salt=username+staticSalt)
	return h

def loggedIn():
	return False

#validate an SSN. return True if valid and False if not
def validSSN(ssn):
    if re.match("^\d{3}-?\d{2}-?\d{4}$", ssn): # XXX-XX-XXXX
        return True
    return False

# whats the criteria for valid username? just if it doesnt already exist? - jimmy 
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

def validFirst(first):
	if first:
		return True
	else:
		return False

def validLast(last):
	if last:
		return True
	else:
		return False

def validAddress(address):
	if address:
		return True
	else:
		return False

def validPhoneNumber(number):
    if re.match("^\d{3}-?\d{3}-?\d{4}$", number): # XXX-XXX-XXXX
        return True
    return False

def validBirthday(dob):
    if re.match("^\d{4}-?\d{2}-?\d{2}$", number): # YYYY-MM-DD
        return True
    return False

def validParty(party):
	if party:
		return True
	else:
		return False

