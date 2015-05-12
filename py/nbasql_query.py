#!/usr/bin/python
import sqlite3
import cgi

if __name__ == '__main__':
  print '<html>'  
  print '<head>'
  print '<!-- DataTables -->'
  print '<link rel="stylesheet" type="text/css" href="http://neurocoding.info/css/jquery.dataTables.css">'
  print '<script type="text/javascript" src="http://neurocoding.info/js/jquery.min.js"></script>'
  print '<script type="text/javascript" src="http://neurocoding.info/js/jquery.dataTables.min.js"></script>'
  print "<script> $(document).ready(function() { $('#sql_result').DataTable({}); } ); </script>"
  print '</head>\n<body>'
  # LOAD DATA
  #DBPATH = '/home/gmf/Code/repos/nba/'
  DBPATH = '/var/www/data/db'
  teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA', 'Vancouver Grizzlies':'VAN', 'Seattle SuperSonics':'SEA', 'Washington Bullets':'WSB'}
  conn = sqlite3.connect(DBPATH + '/nbaJSON.db')
  c = conn.cursor()
  #query = 'select * from Games;'   # get query from form
  form = cgi.FieldStorage()  
  query = form["sql_query"] # + SANITIZE THIS!!
  print query # DEBUG
  results = c.execute(query).fetchall()
  print '<table id="sql_result" class="display" cellspacing="0" width="30%">'
  names = list(map(lambda x: x[0], c.description))
  print '<thead><tr>'
  for n in names:
    print '<th>' + n + '</th>'
  print '</tr></thead>'
  print '<tbody>'
  Ncol = len(names)
  for r in results:
    print '<tr>'
    for j in range(0,Ncol):
      r0 = str(r[j])
    print '<td>' + r0 + '</td>'
    print '</tr>'
  print '</tbody>'
  print '</table>'
  print '</body>'
  print '</html>'