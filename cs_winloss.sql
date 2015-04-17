create view Celtics14 as
select gamedate,  q1+q2 as half, total from QtrScores where team="BOS";

create view Opp14 as
select gamedate,  team as opp, q1+q2 as ohalf, total as ototal from QtrScores where (away="BOS" or home="BOS") and team!="BOS";

create view Celtics15 as
select c.gamedate,o.opp,c.half,o.ohalf,c.total,o.ototal,(c.total>o.ototal) as win from Celtics14 c, Opp14 o where c.gamedate=o.gamedate;

-- compute wins/losses before and after rondo trade (20141219)
select count(win) as W, count(gamedate)-sum(win) as L from Celtics15 where date<20141219;
select count(win) as W, count(gamedate)-sum(win) as L from Celtics15 where date<20141219 and half>ohalf;
select count(win) as W, count(gamedate)-sum(win) as L from Celtics15 where date<20141219 and half<ohalf;
select count(win) as W, count(gamedate)-sum(win) as L from Celtics15 where date<20141219 and half>ohalf;
select count(win) as W, count(gamedate)-sum(win) as L from Celtics15 where date>=20141219;
select count(win) as W, count(gamedate)-sum(win) as L from Celtics15 where date>=20141219 and half>ohalf;
select count(win) as W, count(gamedate)-sum(win) as L from Celtics15 where date>=20141219 and half<ohalf;
select count(win) as W, count(gamedate)-sum(win) as L from Celtics15 where date>=20141219 and half>ohalf;
