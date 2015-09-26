<?php
  // query database
  $db = new SQLite3('nba.db');
  $results = $db->query($_POST["sql_query"]);

  // start header
  echo "<head>\n";

  // build HTML table with basic javascript for DataTable
  // here are css & javascript links
  echo '<!-- DataTables -->';
  echo '<link rel="stylesheet" type="text/css" href="http://neurocoding.info/css/jquery.dataTables.css">';
  echo '<script type="text/javascript" src="http://neurocoding.info/js/jquery.min.js"></script>';
  echo '<script type="text/javascript" src="http://neurocoding.info/js/jquery.dataTables.min.js"></script>';
  
  // javascript to create DataTable after page loads
  echo "<script> $(document).ready(function() { $('#sql_result').DataTable({}); } ); </script>";

  // end header, start body
  echo "</head>\n<body>";

  // make HTML table
  echo '<table id="sql_result" class="display" cellspacing="0" width="30%">';
  // <thead> has data headers
  // for each column, add <th> COLUMN NAME </th>
  echo '<thead><tr>';
  for ($i = 0; $i <= $results->numColumns()-1; $i++) {
    echo "<th>" . $results->columnName($i) . "</th>";
  }
  echo '</tr></thead>';
  // <tbody> has data
  echo '<tbody>';
  while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
    echo '<tr>';
    foreach($row as $field) {
    echo "<td>" . $field . "</td>\n";
    }
    echo "</tr>\n";
  }  
  echo '</tbody>';
  echo '</table>';
  echo '</body>';
?>
