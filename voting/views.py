from flask import Flask, render_template, request, redirect, abort, session, Blueprint

views = Blueprint('views', __name__)

@views.route("/", methods=["GET", "POST"])
def home():
	#return "Welcome to our voting web app!"
	return render_template("index.html")

#@views.route("/css/<file>")
#def serveCSS():
#	return render_template()

@views.route("/about")
def about():
	return "This is a super duper secure voting web app"

