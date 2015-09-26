.open nba3.db
create view Shots14_All as select player,count(made) as sum_fga from Shots where season=2014 group by player;
create view Shots14_5ft as select player,count(made) as sum_fga from Shots where dist<=5 and season=2014 group by player;
create view Shots14_10ft as select player,count(made) as sum_fga from Shots where dist<=10 and dist>5 and season=2014 group by player;
create view Shots14_15ft as select player,count(made) as sum_fga from Shots where dist<=15 and dist>10 and season=2014 group by player;
create view Shots14_20ft as select player,count(made) as sum_fga from Shots where dist<=20 and dist>15 and season=2014 group by player;
create view Shots14_far as select player,count(made) as sum_fga from Shots where dist>20 and season=2014 group by player;

select a.player,a.sum_fga as fga_total,b.sum_fga as fga_5ft, c.sum_fga as fga_10ft, d.sum_fga as fga_15ft, e.sum_fga as fga_20ft, f.sum_fga as fga_21ft from Shots14_All a, Shots14_5ft b, Shots14_10ft c, Shots14_15ft d, Shots14_20ft e, Shots14_far f where a.player=b.player and b.player=c.player and c.player=d.player and d.player=e.player and e.player=f.player; 
