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

			return render_template("vote.html", logged_in=True, voted=True, show_results=True)

	#there is no election today
	return render_template("vote.html", logged_in=True, show_results=False)

#perform the vote by updating database
def vote():
	return ""

#return a list of the candidates running in the given election
def getCandidates(election):
	return []

def getCandidateVotes(candidate):
	return []

#get who did and did not vote in the given election
#this should be sorted alphabetically
def getVoters(election):
	return [], []
