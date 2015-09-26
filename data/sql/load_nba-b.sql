.mode csv

create table Games (gameid varchar(16), season integer, away varchar(3), home varchar(3));
.headers off
.import games_bbref_all.csv Games

create table Scores (gameid varchar(16), gameid_num varchar(32), season integer, away varchar(3), home varchar(3), 
  team varchar(3), player varchar(255), pos varchar(2), min varchar(16), fgm integer, fga integer,
  x3pm integer, x3pa integer, ftm integer, fta integer, pm integer, oreb integer, dreb integer,
  treb integer, ast integer, pf integer, stl integer, tov integer, bs integer, ba integer, pts integer
);
.headers off
.import scores_bbref_all.csv Scores

create table QtrScores (gameid varchar(16), gamedate integer, season integer, away varchar(3), home varchar(3), team varchar(3), q1 integer, q2 integer, q3 integer, q4 integer, ot1 integer, ot2 integer, ot3 integer, ot4 integer, ot5 integer, total integer);
.headers off
.import qtrscores_bbref_all.csv QtrScores


--create table Plays (gameid varchar(16), gameid_num varchar(32), eventid integer, prd integer, 
--  msg_type integer, action_type integer, away_score integer, home_score integer, team varchar(3),
--  game_clock varchar(255), player varchar(255), play varchar(512) 
--);
--.headers off
--.import plays_nba_all.csv Plays
