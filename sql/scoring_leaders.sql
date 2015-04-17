-- print NBA individual scoring leaders for 2014-15 season
select player,round(avg(pts),1) as avgpts from Scores where player!="total" and season=2014 and min>0 group by player having count(min>0)>=41 order by avgpts desc limit 10;
