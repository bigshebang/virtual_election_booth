from flask import Flask, render_template, request, redirect, abort, session, Blueprint

auth = Blueprint('auth', __name__)

@auth.route("/register")
def register():
	return "This is the registration page"

@auth.route("/login")
def login():
	return "This is the login page"

@auth.route("/logout")
def logout():
	return "This is the logout page"

