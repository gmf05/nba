-- compute offensive efficiency (OE) defined as
-- fgm+ast / (fga+ast-oreb+tov) by Shea & Baker, Basketball Analytics (2014)
.open nba.db
select team as Team, sum(pts) as TotalPts, round(cast(sum(fgm) as float)/sum(fga),3) as FGpct, sum(ast) as TotalAst, sum(oreb) as TotalOReb, sum(tov) as TotalTO, round(cast(sum(fgm) + sum(ast) as float)/(sum(fga)+sum(ast)-sum(oreb)+sum(tov)),3) as OE from Scores where season=2014 and player="total" group by team;
