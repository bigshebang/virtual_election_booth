from flask import Flask, render_template, request, redirect, abort, session, Blueprint
from voting.utils import loggedIn, getCurElection, tryLogin

views = Blueprint('views', __name__)

@views.route("/", methods=["GET"])
def home():
	curElection = getCurElection()
	return render_template("index.html", logged_in=loggedIn(), show_results=curElection)

@views.route("/election", methods=["GET"])
def election_page():
	if not loggedIn(): #not logged in, make em register
		return redirect("/register")

	#instead of just getting the current election, we want to be able to get any election
	#we should be able to do a drop down on the page and use the IDs of the elections to choose
	#which one we want to display
	if "election" in request.form.keys():
		if validElectionID(request.form["election"]):
			curElection = request.form["election"]
		else: #election id isn't a number
			error = "Election must be a number."
			return render_template("election.html", logged_in=True, show_results=getCurElection(),
									error=error)
	else:
		curElection = getCurElection()

	if curElection:
		candidates = getCandidates(curElection) #get candidates in election

		#get votes for each candidate
		votes = ()
		for c in candidates:
			votes.append(getCandidateVotes(curElection, c))

		voted, notVoted = getVoters(curElection)
		return render_template("election.html", logged_in=True, show_results=True,
								results=[candidates, votes], voted=voted, notVoted=notVoted)
	else: #election not found, return to home page
		 #they gave us an id to find a given election but we didn't find it
		if request.form["election"]:
			error = "Election not found."
			curElection = getCurElection() #need to check if there's an election today
		else: #there isn't an election today
			error = "No election today."
		return render_template("election.html", logged_in=True, show_results=curElection,
								error=error)

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
					vote(curElection, voted=False)
				else:
					candidate = request.form["candidate"][-1] #get the candidate temp ID
					vote(curElection, candidate=candidates[candidate])

			if result: #vote is valid
				return render_template("vote.html", logged_in=True, voted=True, show_results=True)
			else: #vote is invalid
				if not error:
					error = "There was a problem with your vote. Please try again."

				return render_template("vote.html", logged_in=True, error=error, show_results=True)

	#there is no election today
	return render_template("vote.html", logged_in=True, show_results=False)

#perform the vote by updating database. return true if successful, false if not
def vote(election, candidate=None, voted=True):
	#when we create an election, we need to create the corresponding rows in electionData
	#because this function will assume they're just there

	#shouldn't actually need this
	#verify that the election is still active
	# curTime = getCurTime()
	# if not electionActive(election, curTime):
	# 	return False

	#update mysql db
	#WE NEED to use a mutex or lock so that only one process can ever perform this update on the db
	if voted:
		#update electionData by adding 1 to the vote count for the given condition and add voter
		#to the voterHistory table with the proper data
		pass
	else: #failed vote
		#add the vote to voterHistory table but set the voted value to false
		pass

	return False

#make sure a given election ID is a number and represents a valid election_id
def validElectionID(num):
	if num.isdigit():
		#make sure value is in bounds before returning true
		return True

	return False

#make sure candidate ID given for this election is valid
def validCandidateID(election, candidate):
	return True

#given an election and current time, see if that election is still active
#WE MAY NOT NEED THIS
def electionActive(election, curTime):
	return True

#return a list of the candidates running in the given election
#this MUST be ordered alphabetically by first name
def getCandidates(election):
	return []

#get the number votes for a given candidate in a given election
def getCandidateVotes(election, candidate):
	return []

#get who did and did not vote in the given election
#this should be sorted alphabetically
#if we want to get fancy, we'll do alphabetical, then put the current user at the top
def getVoters(election):
	return [], []
