<?php
$servername = "localhost";
$username = "uname";
$password = "password";
$dbname = "sensedb";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// sql to create table
$sql = "CREATE TABLE sensetable (
id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
temp VARCHAR(30),
humi VARCHAR(30),
pres VARCHAR(30),
)";

if ($conn->query($sql) === TRUE) {
  echo "sensetable successfully";
} else {
  echo "Error creating table: " . $conn->error;
}

$conn->close();
?>
