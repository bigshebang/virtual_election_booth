from flask import Flask, render_template, request, redirect, abort, session, Blueprint
import re
from voting.utils import loggedIn, getCurElection, validAge, db, tryLogin, hashPass, votedAlready

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["GET", "POST"])
def register_page():
	#if user is logged in already, just send them to the home page
	if loggedIn():
		return redirect("/")

	curElection = getCurElection() #get today's election

	if request.method == "GET":
		return render_template("register.html", logged_in=False)
	elif request.method == "POST":
		#validate POST data
		error = None
		result = False
		if not validUsername(request.form['username']):
			error = "You must supply a valid username."
		elif not validPass(request.form['password']):
			error = "Password is invalid."
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
		elif not validSSN(request.form['ssn']):
			error = "You must supply a valid Social Security Number."
		else:
			result = registerUser(request.form)

		#if successful registration
		if result:
			#setup session and bring em back to the home page
			setupSession(request.form["username"])
			return redirect("/")
		else: #failed registration
			if not error:
				error = "Registration failed. Please try again."

			return render_template("register.html", error=error, logged_in=False)

@auth.route("/", methods=["POST"])
def login():
	#if user is logged in already, just send them to the home page
	if loggedIn():
		return redirect("/")

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
		curElection = getCurElection() #get today's election
		voted = votedAlready(curElection, session["id"])
		return render_template("index.html", logged_in=True, election_happening=curElection,
							    voted=voted)
	else: #failed login
		if not error:
			error = "Invalid username/password combination. Try again."

		return render_template("index.html", error=error, logged_in=False)

@auth.route("/logout")
def logout():
	#clear session and put em back to the home page
	if loggedIn():
		session.clear()

	return redirect("/")

def registerUser(data):
	#register user and return success or failure
	password = hashPass(data['password'], data['username']) #hash and salt password

	#get cursor and add user to voters table
	cur = db.connection.cursor()
	# check current number of users 
	cur.execute("SELECT * from voters")
	numVoters = len(cur.fetchall())

    	# register new user
	cur.execute("INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, " +
				"address, phoneNumber, politicalParty) VALUES (%s, %s, %s, %s, %s, " +
				"%s, %s, %s, %s)", [data['ssn'], data['username'], password,
				data['first'], data['last'], data['birthday'], data['address'], data['number'],
				data['party']])
	db.connection.commit()

	# check new number of users 
	# should be 1 more than previous, means registration successful 
	cur.execute("SELECT * from voters;")
	newNumVoters = len(cur.fetchall())

	# since its an insert idk if there will be any results 
	# might have to do select before and after, then compare 
	if (numVoters + 1) == newNumVoters:  
		return True
	else:
		return False

#get data about the given user and put it into the session data
def setupSession(username):
	try:
		session.regenerate()
	except:
		pass #some objects don't have regenerate

	#get relevant user data
	userData = getUserData(username)

	#put username and other data into session
	session["username"] = username
	session["ssn"] = userData["ssn"]
	session["id"] = userData["id"]
	session["firstname"] = userData["first"]
	session["lastname"] = userData["last"]

#get certain user data and return in a dictionary
def getUserData(username):
	data = {}
	#get the ssn, id, firstname, lastname.
	cur = db.connection.cursor()
	cur.execute("SELECT ssn,voter_id,firstname,lastname FROM voters WHERE username = %s",
				[username])
	result = cur.fetchall()

	data["ssn"] = result[0][0]
	data["id"] = result[0][1]
	data["first"] = result[0][2]
	data["last"] = result[0][3]
	return data

#validate an SSN. return True if valid and False if not
#should we do a check to make sure the SSN isn't a duplicate? this way we can tell the user
#otherwise we have no way of really knowing since we won't get a message from the db call
def validSSN(ssn):
	if ssn:
		if re.match("^\d{3}-\d{2}-\d{4}$", ssn): # XXX-XX-XXXX
			cur = db.connection.cursor()
			cur.execute("SELECT * FROM voters WHERE ssn = %s", [ssn])
			result = cur.fetchall()
			if len(result) == 0: # ssn not in db
				return True

	return False

#what is our policy for this? letters, numbers. then one underscore and/or dash?
#allow numbers also
#also do a database check to make sure the username isn't taken
def validUsername(user):
	if user:
		underscore = 0
		dash = 0
		letters = 0
		for c in user:
			charNum = ord(c)
			if c.isdigit():
				pass
			elif c == "-":
				dash += 1
			elif c == "_":
				underscore += 1
			elif not isUpper(charNum) and not isLower(charNum):
				return False
			else:
				letters += 1

			#if too many dashes or underscores
			if dash > 1 or underscore > 1 or letters < 1:
				return False

		#see if username already exists
		cur = db.connection.cursor()
		cur.execute("SELECT * FROM voters WHERE username = %s", [user])
		result = cur.fetchall()

		#username doesn't exist, we're finally good!
		if len(result) == 0:
			return True

	return False

#make policy for min 8 char passwordddddd with at least 1 upper, lower and number
def validPass(password):
	if password: #make sure password isn't blank
		if len(password) >= 8: #make sure at least 8 chars long
			upCount = 0
			lowCount = 0
			numCount = 0

			for c in password: #count number of different characters in password
				if c.isdigit(): #is a number
					numCount += 1
				else: #not a number
					charNum = ord(c)
					if isUpper(charNum): #if uppercase letter
						upCount += 1
					elif isLower(charNum): #if lowercase letter
						lowCount += 1

				if upCount > 0 and lowCount > 0 and numCount > 0:
					return True

	return False

#return true if uppercase letter and false if not
def isUpper(charNum):
	#test if between ascii decimal values for A-Z
	if charNum >= 65 and charNum <= 90:
		return True
	else:
		return False

#return true if lowercase letter and false if not
def isLower(charNum):
	#test if between ascii decimal values for a-z
	if charNum >= 97 and charNum <= 122:
		return True
	else:
		return False

#make sure first name is valid (letters, dashes, apostrophes)
def validFirst(first):
	if re.match("^[A-Za-z\-\s']+$", first): #matches upper, lower, whitespace, and dashes
		return True

	return False

#make sure last name is valid (letters, dashes, apostrophes)
def validLast(last):
	if re.match("^[A-Za-z\-\s']+$", last): #matches upper, lower, whitespace, and dashes
		return True

	return False

#make sure the address consists of letters (1+), numbers (1+) and spaces (1+?)
def validAddress(address):
	letters = 0
	numbers = 0
	space = 0
	for c in address:
		charNum = ord(c)
		if c.isdigit():
			numbers += 1
		elif isLower(charNum) or isUpper(charNum):
			letters += 1
		elif c.isspace():
			space += 1
		if letters >= 1 and numbers >= 1 and space >= 1:
			return True

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
		if re.match("^\d{4}-\d{1,2}-\d{1,2}$", dob): # YYYY-MM-DD
			#make sure they're 18 or older
			if validAge(dob):
				return True

	return False
