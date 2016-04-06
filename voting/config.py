import os

##### GENERATE SECRET KEY #####
with open('.voting_secret_key', 'a+') as secret:
	secret.seek(0)  # Seek to beginning of file since a+ mode leaves you at the end and w+ deletes the file
	key = secret.read()
	if not key:
		key = os.urandom(64)
		secret.write(key)
		secret.flush()

#get private key from file
with open(".recaptcha_private_key", "r") as f:
	recaptchaKey = f.read()

##### SERVER SETTINGS #####
SECRET_KEY = key
#database settings
MYSQL_HOST = "localhost"
MYSQL_USER = "ec-dba"
MYSQL_PASSWORD = "mysql:Password!"
MYSQL_DB = "ElectionCentral"

#for hashing
HASHING_METHOD = "sha512"
HASHING_ROUNDS = 1000000

#other Flask  stuff
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "/tmp/flask_session"
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 86400 # 1 day in seconds
#PERMANENT_SESSION_LIFETIME = 604800 # 7 days in seconds
HOST = "localhost"
#UPLOAD_FOLDER = os.path.normpath('static/uploads')
TRUSTED_PROXIES = ['^127\.0\.0\.1$']
