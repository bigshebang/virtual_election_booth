from flask import Flask, render_template, request, redirect, abort, session, Blueprint
# from flask.ext.mysqldb import MySQL
from threading import Lock
from voting.utils import loggedIn, getCurElection, getLastElection, tryLogin, getDBTimestamp, getUnixTimestamp, db, getCurTime

views = Blueprint('views', __name__)
mutex = Lock()

@views.route("/", methods=["GET"])
def home():
	election_happening = getCurElection()

	if loggedIn():
		voted = votedAlready(election_happening, session["id"])
	else:
		voted = False

	return render_template("index.html", logged_in=loggedIn(), voted=voted,
						   election_happening=election_happening)

@views.route("/election", methods=["GET"])
def election_page():
	if not loggedIn(): #not logged in, make em register
		return redirect("/register")

	#get all previous election IDs and names
	prior = getElections()

	#if user has requested a certain election
	if "prior_election" in request.args.keys():
		prior_election = request.args.get("prior_election")
		if validElectionID(prior_election):
			curElection = int(prior_election)
		else: #election id isn't a number
			error = "Election must be a valid number."
			return render_template("election.html", logged_in=True, prior_elections=prior,
									error=error, election_happening=getCurElection())
	else:
		curElection = getLastElection()

	if curElection:
		electionName = getElectionName(curElection) #get name of selected/current election
		candidates = getCandidates(curElection) #get candidates in election

		#get votes for each candidate
		results = []
		for cid,c in candidates:
			votes = int(getCandidateVotes(curElection, cid))
			results.append((c, votes))

		voted, notVoted = getVoters(curElection)
		return render_template("election.html", logged_in=True, current_election=electionName,
								results=results, voted=voted, notVoted=notVoted,
								prior_elections=prior, election_happening=getCurElection())
	else: #election not found, return to home page
		 #they gave us an id to find a given election but we didn't find it
		if request.args.get("election"):
			error = "Election not found."
		else: #there isn't an election today
			error = "No election today."

		return render_template("election.html", logged_in=True, error=error,
							   election_happening=getCurElection(), prior_elections=prior)

@views.route("/vote", methods=["GET", "POST"])
def vote_page():
	if not loggedIn(): #not logged in, make em register
		return redirect("/register")

	#setup voted variable
	voted = False

	if request.method == "GET":
		curElection = getCurElection()

		if curElection:
			voted = votedAlready(curElection, session["id"])

			if not voted: #didn't vote yet
				candidates = getCandidates(curElection)
				return render_template("vote.html", logged_in=True, election_happening=True,
										listLen=len(candidates), ticket=candidates, voted=False)
			else: #already voted
				return render_template("vote.html", logged_in=True, election_happening=True,
										voted=True)
	elif request.method == "POST":
		#user voted, now we need to process the data if there's an election today
		curElection = getCurElection()

		#when this if statement is true, the election being voted in today is valid
		if curElection:
			voted = votedAlready(curElection, session["id"])
			if not voted: #make sure they didn't vote yet
				candidates = getCandidates(curElection)

				error = None
				result = False
				candidate_id = request.form["candidate"]
				#user should also put their password in to vote
				data = {"username" : session["username"], "password" : request.form["password"]}
				if not tryLogin(data):
					error = "Invalid password."
				elif not validCandidateID(curElection, candidate_id): 
					error = "Invalid candidate ID given. Voter fraud detected - not counting vote."
				else:
					result = vote(curElection, candidate_id, userid=session["id"])

				if result: #vote is valid
					return redirect("/")
				else: #vote is invalid
					if not error:
						error = "There was a problem with your vote. Please try again."

					return render_template("vote.html", logged_in=True, error=error, voted=False,
										   election_happening=True, candidates=candidates)

	#there is no election today or they already voted
	return render_template("vote.html", logged_in=True, election_happening=curElection,
						   voted=voted)

#perform the vote by updating database. return true if successful, false if not
def vote(election, candidate=None, voted=True, userid=""):
	#when we create an election, we need to create the corresponding rows in electionData
	#because this function will assume they're just there

	mutex.acquire() #get the mutex

	try:
		#prep for mysql stuff later on
		timestamp = getDBTimestamp(getCurTime()) #get a mysql datetime value of the current datetime
		cur = db.connection.cursor() #get our mysql cursor

		#if user already voted in this election return false
		#we're checking this before calling this function so we should be able to remove this
		if votedAlready(election, userid):
			return False

		#update mysql db
		if voted:
			#should we wrap all of the mysql statements in try/catch blocks in case there's an error?
			#update electionData by adding 1 to the vote count for the given condition
			cur.execute("UPDATE electionData SET num_votes=num_votes+1 WHERE election_id = %s" +
						" AND candidate_id = %s", [election, candidate])
			db.connection.commit()
			result = cur.fetchall()

			#add voter to the voterHistory table with voted=1
			cur.execute("INSERT INTO voterHistory (election_id, voter_id, time_stamp, voted) VALUES" +
						" (%s, %s, %s, 1)", [election, userid, timestamp])
			db.connection.commit()
			result = cur.fetchall()
			return True
		else: #failed vote
			#add the vote to voterHistory table but set the voted value to false
			cur.execute("INSERT INTO voterHistory (election_id, voter_id, time_stamp, voted) VALUES" +
						" (%s, %s, %s, 0)'", [election, userid, timestamp])
			result = cur.fetchall()
	except: #in case we error, we want internal server error or debugger
		raise
	finally: #no matter what, release mutex
		mutex.release()

	return False

#check if a given user voted in a given election already
def votedAlready(election, userid):
	cur = db.connection.cursor()
	cur.execute("SELECT * FROM voterHistory WHERE election_id = %s AND voter_id = %s",
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
		cur.execute("SELECT * FROM elections WHERE election_id = %s AND end_date <= %s",
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
		cur.execute("SELECT * FROM electionData WHERE election_id = %s and candidate_id = %s",
					[election, candidate])
		result = cur.fetchall()
		if result:
			return True
	return False

#get and return all of the election IDs and names for elections that are over
def getElections():
	timestamp = getDBTimestamp(getCurTime()) #get today in mysql datetime format
	cur = db.connection.cursor()
	cur.execute("SELECT election_id, name FROM elections WHERE end_date <= %s", [timestamp])
	results = cur.fetchall()

	#populate our data structure
	prior_elections = [] # list of tuples (eid, name)
	for (eid, name) in results:
		prior_elections.append((eid,name))

	return prior_elections

#return a list of the candidates running in the given election
# return list of tuples (id, candidate name, position)
def getCandidates(election):
	#get cursor and data from table
	cur = db.connection.cursor()
	# cur.execute("SELECT candidate_id, positio FROM electionData JOIN elections ON electionData.election_id = elections.election_id WHERE electionData.election_id = %s", [election])
	cur.execute("SELECT candidate_id FROM electionData WHERE election_id = %s", [election])
	results = cur.fetchall()
	candidates = []
	for candidate_id in results:
		cur.execute("SELECT firstname, lastname FROM candidates WHERE candidate_id = %s",
					[candidate_id])
		res = cur.fetchall()
		candidate_name = res[0][0] + " " + res[0][1]
		candidates.append((int(candidate_id[0]), candidate_name))

	return candidates

#get the number votes for a given candidate in a given election
def getCandidateVotes(election_id, candidate_id):
	#get cursor and number of votes for given candidate
	cur = db.connection.cursor()
	cur.execute("SELECT num_votes FROM electionData WHERE election_id = %s AND candidate_id =" +
				" %s", [election_id, candidate_id])
	result = cur.fetchall()

	#if there's a result, return it
	if len(result) > 0:
		return result[0][0]
	else:
		return 0

#get who did and did not vote in the given election
#this should be sorted alphabetically
def getVoters(election_id):
	voted = []
	notVoted = []
	#get cursor and data from table
	cur = db.connection.cursor()
	#get those who voted
	cur.execute("SELECT DISTINCT firstname,lastname FROM voters WHERE voter_id IN (SELECT " +
				"voter_id FROM voterHistory WHERE election_id = %s AND voted = 1) ORDER BY " +
				"firstname,lastname", [election_id])
	result = cur.fetchall()

	for voter in result:
		voter_name = voter[0] + " " + voter[1]
		voted.append(voter_name)

	#get those who didn't vote
	cur.execute("SELECT DISTINCT firstname,lastname FROM voters WHERE voter_id NOT IN (SELECT " +
				"voter_id FROM voterHistory WHERE election_id = %s AND voted = 1) ORDER BY " +
				"firstname,lastname", [election_id])
	result2 = cur.fetchall()

	for voter in result2:
		voter_name = voter[0] + " " + voter[1]
		notVoted.append(voter_name)

	#process results from result and result2
	return voted, notVoted

#given an election id, get and return the name of the election
def getElectionName(election_id):
	cur = db.connection.cursor()
	cur.execute("SELECT name FROM elections WHERE election_id = %s", [election_id])
	results = cur.fetchall()

	if len(results) > 0:
		return results[0][0]
	else:
		return None
