from flask import Flask, render_template, request, redirect, abort, session, Blueprint
# from flask.ext.mysqldb import MySQL
from threading import Lock
from voting.utils import loggedIn, getCurElection, getLastElection, tryLogin, getDBTimestamp, getUnixTimestamp, db

views = Blueprint('views', __name__)
mutex = Lock()

@views.route("/", methods=["GET"])
def home():
	curElection = getCurElection()
	return render_template("index.html", logged_in=loggedIn(), show_results=curElection)

@views.route("/election", methods=["GET"])
def election_page():
	if not loggedIn(): #not logged in, make em register
		return redirect("/register")

	#get all previous election IDs and names
	prior = getElections()

	if "election" in request.form.keys():
		if validElectionID(request.args.get("election")):
			curElection = request.args.get("election")
		else: #election id isn't a number
			error = "Election must be a number."
			return render_template("election.html", logged_in=True, prior_elections=prior,
									show_results=getCurElection(), error=error)
	else:
		curElection = getLastElection()

	if curElection:
		candidates = getCandidates(curElection) #get candidates in election

		#get votes for each candidate
		votes = ()
		for c in candidates:
			votes.append(getCandidateVotes(curElection, c))

		voted, notVoted = getVoters(curElection)
		return render_template("election.html", logged_in=True, show_results=True,
								results=[candidates, votes], voted=voted, notVoted=notVoted,
								prior_elections=prior)
	else: #election not found, return to home page
		 #they gave us an id to find a given election but we didn't find it
		if request.args.get("election"):
			error = "Election not found."
		else: #there isn't an election today
			error = "No election today."
		return render_template("election.html", logged_in=True, show_results=getCurElection(),
								error=error, prior_elections=prior)

@views.route("/vote", methods=["GET", "POST"])
def vote_page():
	if not loggedIn(): #not logged in, make em register
		return redirect("/register")

	if request.method == "GET":
		curElection = getCurElection()
		if curElection:
			candidates = getCandidates(curElection)
			return render_template("vote.html", logged_in=True, show_results=True,
									listLen=len(candidates), candidates=candidates)
	elif request.method == "POST":
		#user voted, now we need to process the data if there's an election today
		curElection = getCurElection()

		#when this if statement is true, the election being voted in today is valid
		if curElection:
			candidates = getCandidates(curElection)

			error = None
			result = False
			#user should also put their password in to vote
			if not tryLogin(session["username"], request.form["password"]):
				error = "Invalid password."
			elif not validCandidateID(curElection, request.form["candidate"]):
				error = "Invalid candidate ID given. Voter fraud detected - not counting vote."
			else:
				#if candidate id is out of bounds for this election then this is a malicious voting
				#attempt. don't count the vote, but record the invalid vote.
				if candidate >= len(candidates):
					vote(curElection, voted=False, userid=session["id"])
				else:
					candidate = request.form["candidate"][-1] #get the candidate temp ID
					vote(curElection, candidate=candidates[candidate], userid=session["id"])

			if result: #vote is valid
				return render_template("vote.html", logged_in=True, voted=True, show_results=True)
			else: #vote is invalid
				if not error:
					error = "There was a problem with your vote. Please try again."

				return render_template("vote.html", logged_in=True, error=error, show_results=True)

	#there is no election today
	return render_template("vote.html", logged_in=True, show_results=False)

#perform the vote by updating database. return true if successful, false if not
def vote(election, candidate=None, voted=True, userid=""):
	#when we create an election, we need to create the corresponding rows in electionData
	#because this function will assume they're just there

	mutex.acquire() #get the mutex

	#prep for mysql stuff later on
	timestamp = getDBTimestamp(getCurTime()) #get a mysql datetime value of the current datetime
	cur = db.connection.cursor() #get our mysql cursor

	#if user already voted in this election, release mutex and return false
	if votedAlready(election, userid, cur):
		mutex.release()
		return False

	#update mysql db
	if voted:
		#should we wrap all of the mysql statements in try/catch blocks in case there's an error?
		#update electionData by adding 1 to the vote count for the given condition
		cur.execute("UPDATE electionData SET num_votes=num_votes+1 WHERE election_id = %d" +
					" AND candidate_id = %d", [election, userid])
		result = cur.fetchall()

		#add voter to the voterHistory table with voted=1
		cur.execute("INSERT INTO voterHistory (election_id, voter_id, time_stamp, voted) VALUES" +
					" (%d, %d, %s, 1)'", [election, userid, timestamp])
		result = cur.fetchall()
	else: #failed vote
		#add the vote to voterHistory table but set the voted value to false
		cur.execute("INSERT INTO voterHistory (election_id, voter_id, time_stamp, voted) VALUES" +
					" (%d, %d, %s, 0)'", [election, userid, timestamp])
		result = cur.fetchall()

	mutex.release()
	return False

#check if a given user voted in a given election already
def votedAlready(election, userid, cur):
	cur.execute("SELECT * FROM electionHistory WHERE election_id = %d AND voter_id = %s",
				[election, userid])
	result = cur.fetchall()

	#they have voted before in this election bc they exist in the electionHistory table
	if len(result) > 0:
		return True

	return False

#make sure a given election ID is a number and represents a valid election_id. also check to make
#sure this election is over
def validElectionID(num):
	if num.isdigit():
		timestamp = getDBTimestamp(getCurTime()) #today's timestamp

		#make sure value of num references a valid election that has ended
		cur = db.connection.cursor()
		cur.execute("SELECT * FROM elections WHERE election_id = %d WHERE end_date < %s",
					[num, timestamp])
		result = cur.fetchall()

		if len(result) > 0:
			return True

	return False

#make sure candidate ID given for this election is valid
def validCandidateID(election, candidate):
	if election and candidate: #if non-empty election and candidate
		#what else do we need to check?
		#if we just keep real candidate id throughout everything, we shouldn't need this and
		#everything else should be easier
		cur = db.connection.cursor()
		cur.execute("SELECT * FROM electionData WHERE election_id = %d", [election])
		result = cur.fetchall()

		#candidate can be from 0 up to n-1 (indexing from 0)
		if candidate >= 0 and candidate < len(result):
			return True

	return False

#given an election and current time, see if that election is still active
#WE MAY NOT NEED THIS
def electionActive(election, curTime):
	return True

#get and return all of the election IDs and names for elections that are over
#see getLastElection() in utils.py for help with getting an election that's over
def getElections():
    	cur = db.connection.cursor()
    	cur.execute("SELECT election_id, name FROM elections")
	results = cur.fetchall()
    	prior_elections = [] # list of tuples (eid, name)
    	for (eid, name) in results:
		prior_elections.append((eid,name))
	return prior_elections

#return a list of the candidates running in the given election
#this MUST be ordered alphabetically by first name
def getCandidates(election):
	#get cursor and data from table
	cur = db.connection.cursor()
	# if we want to do ORDER BY we have to use a union or join b\c electionData doesnt have a firstname field 
	# cur.execute("SELECT candidate_id FROM electionData WHERE election_id = %s ORDER BY firstname", [election])
	cur.execute("SELECT candidate_id FROM electionData WHERE election_id = %s", [election])
	results = cur.fetchall()
	candidates = []
	for candidate_id in results:
		cur.execute("SELECT firstname, lastname FROM candidates WHERE candidate_id = %s", [candidate_id])
		res = cur.fetchall()
		candidate_name = result[0][0] + " " + result[0][1]
		candidates.append(candidate_name)
	return candidates

#get the number votes for a given candidate in a given election
def getCandidateVotes(election, candidate):
	#get cursor and number of votes for given candidate
	cur = db.connection.cursor()
	cur.execute("SELECT num_votes FROM electionData WHERE election_id = %s AND candidate_id =" +
				" %s", [election, candidate])
	result = cur.fetchall()

	votes = result[0]
	return votes

#get who did and did not vote in the given election
#this should be sorted alphabetically
#if we want to get fancy, we'll do alphabetical, then put the current user at the top
# --- not getting fancy..
def getVoters(election):
	voted = []
	notVoted = []
	#get cursor and data from table
	cur = db.connection.cursor()
	#get those who voted
	cur.execute("SELECT voter_id FROM voterHistory WHERE election = %s AND voted = 1", [election])
	result = cur.fetchall()
	for voter_id in result:
		cur.execute("SELECT firstname, lastname FROM voters WHERE voter_id = %s", [voter_id])
		r = cur.fetchall()
		voter_name = r[0][0] + " " + r[0][1]
		voted.append(voter_name)
	#get those who didn't vote
	cur.execute("SELECT voter_id FROM voterHistory WHERE election = %s AND voted = 0", [election])
	result2 = cur.fetchall()
	for voter_id in result2:
		cur.execute("SELECT firstname, lastname FROM voters WHERE voter_id = %s", [voter_id])
		r = cur.fetchall()
		voter_name = r[0][0] + " " + r[0][1]
		notVoted.append(voter_name)

	#process results from result and result2
	return voted, notVoted
