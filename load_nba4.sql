create table QtrScores (gameid VARCHAR(16), gamedate integer, away varchar(3), home varchar(3), team varchar(3), q1 integer, q2 integer, q3 integer, q4 integer, ot1 integer, ot2 integer, ot3 integer, total integer);
-- ignore csv headers since they are defined above 
.mode csv
.headers off
.import qtrscores_bbref_00214.csv QtrScores
