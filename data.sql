######################################################################
# script doesnt work but manually copying and pasting into sql works #
# idk why.. sql still dumb                                           #
######################################################################

# Adding fake voter information 
INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, address, phoneNumber, politicalParty) VALUES("123-45-6789", "user1", "wont work", "first", "last", "1990-09-09", "123 st", "111-111-1111", "party");
INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, address, phoneNumber, politicalParty) VALUES("111-22-3333", "user2", "wont work", "name", "friend", "1994-05-05", "1 st", "222-222-2222", "party2");
INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, address, phoneNumber, politicalParty) VALUES("115-52-5335", "user3", "wont work", "jon", "jon", "1993-03-03", "3 st", "333-333-3333", "party3");
INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, address, phoneNumber, politicalParty) VALUES("415-54-5445", "user4", "wont work", "hi", "there", "1991-01-01", "4 st", "444-444-4444", "party4");
INSERT INTO voters (ssn, username, password, firstname, lastname, birthday, address, phoneNumber, politicalParty) VALUES("333-22-4444", "user5", "wont work", "not", "cool", "1988-08-08", "8 st", "888-888-8888", "party8");

# Adding fake candidate information
INSERT INTO candidates (ssn, firstname, lastname, politicalParty) VALUES("443-09-0011", "John", "Deer", "Farm");
INSERT INTO candidates (ssn, firstname, lastname, politicalParty) VALUES("443-09-0011", "Joe", "Smith", "idk");
INSERT INTO candidates (ssn, firstname, lastname, politicalParty) VALUES("443-09-0011", "Sammy", "Cacciatore", "billygoat");


# Adding fake elections
INSERT INTO elections (name, location, start_date, end_date, position) VALUES ("President", "USA", "2016-04-01 12:00:00", "2016-04-30 12:00:00", "President");

# Adding fake election info
INSERT INTO electionData (election_id, candidate_id, num_votes) VALUES (1,1,4);
INSERT INTO electionData (election_id, candidate_id, num_votes) VALUES (1,2,1);
INSERT INTO electionData (election_id, candidate_id, num_votes) VALUES (1,3,7);
INSERT INTO electionData (election_id, candidate_id, num_votes) VALUES (1,4,5);
