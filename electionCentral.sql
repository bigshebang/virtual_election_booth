DROP DATABASE IF EXISTS ElectionCentral;

CREATE DATABASE ElectionCentral;
use ElectionCentral;

CREATE TABLE voterHistory(
	election_id int,
	voter_id int,
	time_stamp datetime,
	voted bit(1) DEFAULT 1,
	CONSTRAINT pk_vote_id PRIMARY KEY (election_id, voter_id)
);

CREATE TABLE voters(
	ssn char(11), # XXX-XX-XXXX
	voter_id int AUTO_INCREMENT,
	username varchar(50),
	password char(128),
	firstname varchar(50),
	lastname varchar(50),
	birthday date, # YYYY-MM-DD
	address varchar(200),
	phoneNumber varchar(12), # XXX-XXX-XXXX
	politicalParty varchar(100),
	isAdmin int(1) DEFAULT 0,
	PRIMARY KEY (voter_id)
);

CREATE TABLE electionData(
	election_id int,
	candidate_id int,
	num_votes int DEFAULT 0,
	CONSTRAINT pk_electionData PRIMARY KEY (election_id, candidate_id)
);

CREATE TABLE elections(
	election_id int AUTO_INCREMENT,
	name varchar(50),
	location varchar(100),
	start_date datetime, # YYYY-MM-DD HH:MI:SS
	end_date datetime, # YYYY-MM-DD HH:MI:SS
	position varchar(50),
    PRIMARY_KEY(election_id),
	FOREIGN KEY (election_id) REFERENCES voterHistory(election_id),
	FOREIGN KEY (election_id) REFERENCES electionData(election_id)
);

CREATE TABLE candidates(
	ssn char(11), # XXX-XX-XXXX
	candidate_id int AUTO_INCREMENT,
	firstname varchar(50),
	lastname varchar(50),
	politicalParty varchar(100),
	PRIMARY KEY (candidate_id)
);

#remove old user and recreate
DELETE FROM mysql.user WHERE User = 'ec-dba'@'localhost';
CREATE USER 'ec-dba'@'localhost' IDENTIFIED BY "mysql:Password!";
GRANT SELECT,INSERT,UPDATE on ElectionCentral.* TO 'ec-dba'@'localhost';
FLUSH PRIVILEGES;

