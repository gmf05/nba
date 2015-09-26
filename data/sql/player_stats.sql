.open nba.db
.mode csv
.headers on
.output "player_stats_2014.csv"
select player, sum(min)/count((min>0)) as min_gm, cast(sum(fgm) as float)/sum(min)*36 as fgm, cast(sum(fga) as float)/sum(min)*36 as fga, cast(sum(x3pm) as float)/sum(min)*36 as x3pm, cast(sum(x3pa) as float)/sum(min)*36 as x3pa, cast(sum(ftm) as float)/sum(min)*36 as ftm, cast(sum(fta) as float)/sum(min)*36 as fta, cast(sum(ast) as float)/sum(min)*36 as ast, cast(sum(oreb) as float)/sum(min)*36 as oreb, cast(sum(dreb) as float)/sum(min)*36 as dreb, cast(sum(stl) as float)/sum(min)*36 as stl, cast(sum(tov) as float)/sum(min)*36 as tov, cast(sum(bs) as float)/sum(min)*36 as bs, cast(sum(pts) as float)/sum(min)*36 as pts, round(cast(sum(fta) as float)/sum(fga),3) as ft_fg, cast(sum(pf) as float)/sum(min)*36 as pf from Scores where season=2014 and player!="total" group by player having sum(min)>0;
