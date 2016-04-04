from flask import Flask, render_template, request, redirect, abort, session, Blueprint

views = Blueprint('views', __name__)

@views.route("/", methods=["GET"])
def home():
	if request.method == "GET":
		return render_template("index.html")

@views.route("/election", methods=["GET"])
def election_page():
	curElection = getCurElection()
	candidates = getCandidates(curElection)
	return render_template("election.html", results=[("", 5)])

@views.route("/vote", methods=["GET", "POST"])
def vote_page():
	if request.method == "GET":
		curElection = getCurElection()
		candidates = getCandidates(curElection)
		return render_template("vote.html", listLen=len(candidates), candidates=candidates)
	elif request.method == "POST":
		#user voted, now we need to process the data
		curElection = getCurElection()
		candidates = getCandidates(curElection)

		return render_template("vote.html", voted=True)

#perform the vote by updating database
def vote():
	return ""

#get the current active election for the day
def getCurElection():
	return ""

#return a list of the candidates running in the given election
def getCandidates(curElection):
	return []
