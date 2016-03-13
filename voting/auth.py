from flask import Flask, render_template, request, redirect, abort, session, Blueprint

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["GET", "POST"])
def register_page():
	if request.method == "GET":
		return render_template("register.html")
	elif request.method == "POST":
		return render_template("register.html")
	else: #weird HTTP method we don't support
		return render_template("index.html")

@auth.route("/", methods=["POST"])
def login():
	return render_template("index.html")

@auth.route("/logout")
def logout():
	#do logout stuff then send em back to home page
	return render_template("index.html")

