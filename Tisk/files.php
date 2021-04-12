<!DOCTYPE html>
<html>
<body>

<h1>My first PHP page</h1>

<?php
echo "Hello World2!<br/>";
echo "line9<br/>";
$f = opendir("..");
$n = 5;
$m = 0;
while ($m<$n){ 
   print ($m);
   $e = readdir($f);
   print($e);
   $m = $m+1;
   }
echo "<a href='george.htm'>george</a>";
?> 

</body>
</html>

