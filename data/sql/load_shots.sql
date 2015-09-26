.mode csv

create table Shots (gameid varchar(16), season integer, gameid_num varchar(10), player varchar(100), team varchar(3), prd integer, min_remain integer, sec_remain integer, pts integer, dist integer, x integer, y integer, made boolean);
.headers off
.import shots_all.csv Shots
