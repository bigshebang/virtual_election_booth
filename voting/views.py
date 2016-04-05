from flask import Flask, render_template, request, redirect, abort, session, Blueprint
from voting.utils import loggedIn, getCurElection

views = Blueprint('views', __name__)

@views.route("/", methods=["GET"])
def home():
	curElection = getCurElection()
	return render_template("index.html", logged_in=loggedIn(), show_results=curElection)

@views.route("/election", methods=["GET"])
def election_page():
	if not loggedIn(): #not logged in, make em register
		return redirect("/register")

	curElection = getCurElection()
	if curElection:
		candidates = getCandidates(curElection) #get candidates in election

		#get votes for each candidate
		votes = ()
		for c in candidates:
			votes.append(getCandidateVotes(c))

		voted, notVoted = getVoters(curElection)
		return render_template("election.html", logged_in=True, show_results=True, results=[candidates, votes], voted=voted, notVoted=notVoted)
	else: #no election today, return to home page
		return redirect("/")

@views.route("/vote", methods=["GET", "POST"])
def vote_page():
	if not loggedIn(): #not logged in, make em register
		return redirect("/register")

	if request.method == "GET":
		curElection = getCurElection()
		if curElection:
			candidates = getCandidates(curElection)
			return render_template("vote.html", logged_in=True, show_results=True, listLen=len(candidates), candidates=candidates)
	elif request.method == "POST":
		#user voted, now we need to process the data
		curElection = getCurElection()
		if curElection:
			candidates = getCandidates(curElection)

			candidate = request.form["candidate"][-1] #get the candidate temp ID

			#if candidate id is out of bounds for this election then this is a malicious voting
			#attempt. don't count the vote, but record the invalid vote.
			if candidate >= len(candidates):
				vote(curElection, voted=False)
			else:
				vote(curElection, candidate=candidates[candidate])

			return render_template("vote.html", logged_in=True, voted=True, show_results=True)

	#there is no election today
	return render_template("vote.html", logged_in=True, show_results=False)

#get the current time in mysql datetime format - YYYY-MM-DD HH:MI:SS
def getCurTime():
	return "2016-04-25 10:00:00"

#perform the vote by updating database. return true if successful, false if not
def vote(election, candidate=None, voted=True):
	#when we create an election, we need to create the corresponding rows in electionData
	#because this function will assume they're just there

	#verify that the election is still active
	curTime = getCurTime()
	if not electionActive(election, curTime):
		return False

	#update mysql db
	#WE NEED to use a mutex or lock so that only one process can ever perform this update on the db
	if voted:
		#update electionData by adding 1 to the vote count for the given condition and add voter
		#to the voterHistory table with the proper data
		pass
	else: #failed vote
		#add the
		pass

	return False

#given an election and current time, see if that election is still active
def electionActive(election, curTime):
	return True

#return a list of the candidates running in the given election
#this MUST be ordered alphabetically by first name
def getCandidates(election):
	return []

def getCandidateVotes(candidate):
	return []

#get who did and did not vote in the given election
#this should be sorted alphabetically
def getVoters(election):
	return [], []
