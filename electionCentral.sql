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
	ssn varchar(11), # XXX-XX-XXXX
	voter_id int,
	username varchar(25),
	password varchar(25),
	firstname varchar(25),
	lastname varchar(25),
	birthday date, # YYYY-MM-DD
	address varchar(50),
	phoneNumber varchar(12), # XXX-XXX-XXXX
	politicalParty varchar(25),
	isAdmin int(1) DEFAULT 0,
	PRIMARY KEY (ssn)
	# FOREIGN KEY (voter_id) REFERENCES voterHistory(voter_id) # says cant add FK.. dont know why
);

CREATE TABLE electionData(
    election_id int,
    candidate_id int,
    num_votes int DEFAULT 0,
	CONSTRAINT pk_electionData PRIMARY KEY (election_id, candidate_id)
);

CREATE TABLE elections(
	election_id int,
	name varchar(50),
	location varchar(50),
	start_date datetime, # YYYY-MM-DD HH:MI:SS
	end_date datetime, # YYYY-MM-DD HH:MI:SS
	position varchar(25),
	FOREIGN KEY (election_id) REFERENCES voterHistory(election_id),
	FOREIGN KEY (election_id) REFERENCES electionData(election_id)
);

CREATE TABLE candidates(
    ssn varchar(11), # XXX-XX-XXXX
    candidate_id int,
    firstname varchar(25),
    lastname varchar(25),
    politicalParty varchar(25),
	PRIMARY KEY (ssn)
    # FOREIGN KEY (candidate_id) REFERENCES electionData(candidate_id) # says cant add FK
);

