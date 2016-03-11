DROP DATABASE IF EXISTS ElectionCentral;

CREATE DATABASE ElectionCentral;
use ElectionCentral;

CREATE TABLE voterHistory(
	election_id int,
	voter_id int,
	time_stamp datetime,
	CONSTRAINT pk_vote_id PRIMARY KEY (election_id, voter_id)
);

CREATE TABLE voters(
	ssn char(11), # XXX-XX-XXXX
	voter_id int,
	username varchar(25),
	password char(128),
	firstname varchar(50),
	lastname varchar(50),
	birthday date, # YYYY-MM-DD
	address varchar(50),
	phoneNumber varchar(12), # XXX-XXX-XXXX
	politicalParty varchar(50),
	isAdmin int(1) DEFAULT 0,
	PRIMARY KEY (ssn)
	# FOREIGN KEY (voter_id) REFERENCES voterHistory(voter_id) # says cant add FK.. dont know why
);

CREATE TABLE electionData(
	election_id int,
	name varchar(50),
	location varchar(50),
	start_date datetime, # YYYY-MM-DD HH:MI:SS
	end_date datetime, # YYYY-MM-DD HH:MI:SS
	position varchar(50),
	FOREIGN KEY (election_id) REFERENCES voterHistory(election_id)
);
