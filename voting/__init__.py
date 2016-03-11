from flask import Flask, render_template, request, redirect, abort, session


def createApp(config="voting.config"):
	#initialize app
	app = Flask("voting")

	with app.app_context():
		app.config.from_object(config)

		#import stuff from this app so we can add blue prints
		from voting.views import views
		from voting.auth import auth

		#register blue print so pages will render
		app.register_blueprint(views)
		app.register_blueprint(auth)

	return app

#@app.route("/")
#def home():
    #return render_template("index.html")
#	return "balls"

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)

#def run():
#	app = Flask("voting")
#	return app

