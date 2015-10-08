#!/usr/bin/python
# query db with SQLite3 and print result as HTML table
import sqlite3
import cgi
import cgitb
cgitb.enable() # helps troubleshoot cgi

# HTML header
print "Content-Type: text/html\n"
print """
<html><head>
<title>Query NBA database via SQL</title>

<!-- Bootstrap core CSS -->
<link href="http://neurocoding.info/css/bootstrap.min.css" rel="stylesheet">

<!-- Custom styles for this template -->
<link href="http://neurocoding.info/css/navbar-fixed-top.css" rel="stylesheet">

<!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
<!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->
<script src="http://neurocoding.info/js/ie-emulation-modes-warning.js"></script>

<!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
<!--[if lt IE 9]>
  <script src="http://neurocoding.info/js/html5shiv.min.js"></script>
  <script src="http://neurocoding.info/js/respond.min.js"></script>
<![endif]-->

<!-- DataTables -->
<link rel="stylesheet" type="text/css" href="http://neurocoding.info/css/jquery.dataTables.css">
<script type="text/javascript" src="http://neurocoding.info/js/jquery.min.js"></script>
<script type="text/javascript" src="http://neurocoding.info/js/jquery.dataTables.min.js"></script>
<script>
$(document).ready(function() {
  $('#tab1').DataTable( {
  "order": [[1, "desc"]]
  });
});
</script>


</head>
<body>
"""

# Form for SQL query:
form = cgi.FieldStorage()
print """
  <form method="post" action="index.cgi">
  <p>Query: <textarea name="query"></textarea><input type="submit" value="Submit"/></p>
  </form>
"""

# Query SQLite DB:
#db_path = '/var/www/data/db'
db_path = '/home/gmf/Code/repos/nba/sql'
conn = sqlite3.connect(db_path + '/nba3.db')
c = conn.cursor()
query = form.getvalue("query","select * from Games where season=2013 limit 10;")
# sanitize query to prevent SQL injection, etc.
c.execute(query)
names = [description[0] for description in c.description]

# print results in HTML table
print '<table id="tab1">'

# table headers
print "<thead><tr>"
for row in names:
  print "<th>" + row + "</th>"
print "</thead>"

# table body
print "<tbody>"
for row in c.fetchall():
    print "<tr>"
    for i in row:
      print "<td>%s</td>" % i
    print "</tr>"
print "</tbody>"
    
print "</table>"
print "</body></html>"

conn.close() # close SQLite connection