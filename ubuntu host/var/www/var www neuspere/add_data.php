<?php
    // Connect to MySQL
include("dbconnect.php");

    // Prepare the SQL statement
      date_default_timezone_set('america/los_angeles');
     $dateS = date('Y/m/d h:i:s', time());
     $temp = $_GET["temp"];
     $humi = $_GET["humi"];
     $pres = $_GET["pres"];

    $SQL = "INSERT INTO sensedb.sensetable (reg_date,temp,humi,pres) VALUES ('".$dateS."','".$temp."','".$humi."','".$pres."');";

    // Execute SQL statement
    mysqli_query($conn,$SQL);
    $SQL = "commit;";

    // Execute SQL statement
    mysqli_query($conn,$SQL);

    // Go to the review_data.php (optional)
    header("Location: sense.php");
?>
