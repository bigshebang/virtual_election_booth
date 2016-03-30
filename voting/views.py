from flask import Flask, render_template, request, redirect, abort, session, Blueprint

views = Blueprint('views', __name__)

@views.route("/", methods=["GET"])
def home():
	if request.method == "GET":
		return render_template("index.html")

@views.route("/vote", methods=["GET", "POST"])
def vote_page():
	if request.method == "GET":
		return render_template("vote.html")
	elif request.method == "POST":
		return render_template("vote.html")
	else: #weird HTTP method we don't support
		return render_template("index.html")

