.mode csv

create table TeamSeasons (season integer, team_name varchar(100), team varchar(3), g integer, mp integer, fg integer, fga integer, fgpct float, x3pm integer, x3pa integer, x3ppct float, x2pm integer, x2pa integer, x2ppct float, ftm integer, fta integer, ftpct float, oreb integer, dreb integer, treb integer, ast integer, stl integer, bs integer, tov integer, pf integer, pts integer, pts_g float, playoffs boolean);
-- ignore csv field headers 
.headers off
.import teamseasons_bbref_all.csv TeamSeasons

create table OppSeasons (season integer, team_name varchar(100), team varchar(3), g integer, mp integer, fg integer, fga integer, fgpct float, x3pm integer, x3pa integer, x3ppct float, x2pm integer, x2pa integer, x2ppct float, ftm integer, fta integer, ftpct float, oreb integer, dreb integer, treb integer, ast integer, stl integer, bs integer, tov integer, pf integer, pts integer, pts_g float, playoffs boolean);
-- ignore csv field headers 
.headers off
.import oppseasons_bbref_all.csv OppSeasons

create table WinLoss (season integer, team_name varchar(100), team varchar(3), g integer, w integer, l integer, w_home integer, l_home integer, w_road integer, l_road integer, w_east integer, l_east integer, w_west integer, l_west integer, w_atl integer, l_atl integer, w_ctl integer, l_ctl integer, w_se integer, l_se integer, w_nw integer, l_nw integer, w_pac integer, l_pac integer, w_sw integer, l_sw integer, w_pre integer, l_pre integer, w_post integer, l_post integer, w_3pt integer, l_3pt integer, w_10pt integer, l_10pt integer, w_oct integer, l_oct integer, w_nov integer, l_nov integer, w_dec integer, l_dec integer, w_jan integer, l_jan integer, w_feb integer, l_feb integer, w_mar integer, l_mar integer, w_apr integer, l_apr integer
);
.headers off
.import winloss_bbref_all.csv WinLoss
