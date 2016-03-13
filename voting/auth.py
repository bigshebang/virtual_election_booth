from flask import Flask, render_template, request, redirect, abort, session, Blueprint
from flask.ext.mysqldb import MySQL

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
		elif not validNumber(request.form['number']):
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
	elif not request.form['plainPass']:
		error = "Password must not be left blank."
	else:
		result = tryLogin(request.form)

	if result:
		return render_template("index.html")
	else:
		if not error:
			error = "Invalid username/password combination. Try again."

		return render_template("index.html", error=error)

@auth.route("/logout")
def logout():
	#do logout stuff then send em back to home page
	return render_template("index.html")

def registerUser(data):
	#register user and return success or failure
	#make data['password'] into hashed and salted version
	#make data['birthday'] into proper format
	#get cursor and add user to voters table
	cur = db.connection.cursor()
	cur.execute("INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, " +
				"address, phoneNumber, politicalParty) VALUES ('%s', '%s', '%s', '%s', '%s', " +
				"'%s', '%s', '%s', '%s')", (data['ssn'], data['username'], data['password'],
				data['first'], data['last'], data['birthday'], data['address'], data['number'],
				data['party']))
	result = cur.fetchall()
	return True

def tryLogin(data):
	return True

#validate an SSN. return True if valid and False if not
def validSSN(ssn):
	if ssn:
		return True
	else:
		return False

def validUsername(user):
	if user:
		return True
	else:
		return False

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

def validNumber(number):
	if number:
		return True
	else:
		return False

def validBirthday(dob):
	if dob:
		return True
	else:
		return False

def validParty(party):
	if party:
		return True
	else:
		return False

