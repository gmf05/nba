--create table Games (gameid VARCHAR(16), season INTEGER, away VARCHAR(3), home VARCHAR(3));
-- make sure names are consistent by ignoring csv field headers
--.headers off
--.mode csv
--.import games_bbref_all.csv Games
--
--create table Scores (gameid VARCHAR(16), gameid_num VARCHAR(32), season INTEGER, away VARCHAR(3), home VARCHAR(3), 
--  team VARCHAR(3), player VARCHAR(255), pos VARCHAR(2), min VARCHAR(16), fgm INTEGER, fga INTEGER,
--  x3pm INTEGER, x3pa INTEGER, ftm INTEGER, fta INTEGER, pm INTEGER, oreb INTEGER, dreb INTEGER,
--  treb INTEGER, ast INTEGER, pf INTEGER, stl INTEGER, tov INTEGER, bs INTEGER, ba INTEGER, pts INTEGER
--);
--.mode csv
-- make sure names are consistent by ignoring csv field headers
--.headers off
--.import scores_bbref_all.csv Scores

.mode csv
create table Plays (gameid VARCHAR(16), gameid_num VARCHAR(32), eventid INTEGER, prd INTEGER, 
  msg_type INTEGER, action_type INTEGER, away_score INTEGER, home_score INTEGER, team VARCHAR(3),
  game_clock VARCHAR(255), player VARCHAR(255), play VARCHAR(512) 
);
-- ignore csv headers since they are defined above 
.headers off
.import plays_nba_all.csv Plays
