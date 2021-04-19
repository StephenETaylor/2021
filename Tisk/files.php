<!DOCTYPE html>
<html>
<head>
<meta charset='UTF8'>
</head>
<body>


<?php
echo "<br/>";

$f = opendir(".");
$n = 10;
$m = 0;
while ($m<$n){ 
   $e = readdir($f);
   if ($e == ".." or $e == "." ){ $m = $m+1; continue; }
   if ($e == "" ){ break; }
   #print ($m);
   echo "<a href='$e'>";
   print($e);
   print("</a><br/>");
   $m = $m+1;
   }
?> 

</body>
</html>

