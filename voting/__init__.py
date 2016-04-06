from flask import Flask, render_template, request, redirect, abort, session
# from flask_wtf.csrf import CsrfProtect

csrf = CsrfProtect()

def createApp(config="voting.config"):
	#initialize app
	app = Flask("voting")
	csrf.init_app(app)

	with app.app_context():
		app.config.from_object(config)

		#import stuff from this app so we can add blue prints
		from voting.views import views
		from voting.auth import auth
		from voting.auth import utils

		#register blue print so pages will render
		app.register_blueprint(views)
		app.register_blueprint(auth)
		app.register_blueprint(utils)

	return app

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)
