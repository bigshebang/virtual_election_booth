from flask import Flask, render_template, request, redirect, abort, session, Blueprint

views = Blueprint('views', __name__)

@views.route("/", methods=["GET"])
def home():
	if request.method == "GET":
		return render_template("index.html")

@views.route("/election", methods=["GET"])
def election_page():
	return render_template("election.html", results=[("", 5)])

@views.route("/vote", methods=["GET", "POST"])
def vote_page():
	if request.method == "GET":
		return render_template("vote.html", listLen=0, candidates=[""])
	elif request.method == "POST":
		#user voted, now we need to process the data
		return render_template("vote.html")
	else: #weird HTTP method we don't support
		return render_template("index.html")

def vote():
	return ""

