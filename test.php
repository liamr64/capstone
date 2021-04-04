<html>
</body>
<?php  
	$servername = "database-1.ceb0m91rauea.us-east-1.rds.amazonaws.com";
	$username = "admin";
	$dbname = "Capstone";
	$password = "1387194#";

	try {
		$conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
		// set the PDO error mode to exception
		$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
		
		
		$lottery = $_GET["lottery"];
		$time = $_GET["time"];
		$people = $_GET["people"];
		$location = $_GET["location"];
		
		echo strcmp($lottery, "Enter Lottery...") != 0;
		if (strcmp($lottery, "Enter Lottery...") != 0 and isset($time) and strcmp($location, "Location...") != 0 and strcmp($people, "Total Number of People") != 0) {
			$query = "SELECT ModelData.probability, Room.RoomName FROM ModelData INNER JOIN Room on ModelData.Room_id INNER JOIN Residence_Hall ON Room.Residence_Hall_idResidence_Hall
					 WHERE ModelData.Time = \"$time\" and Residence_Hall.ResName = \"$location\"";
			$stmt = $conn->prepare($query);
			$stmt->execute();
			// set the resulting array to associative
			$result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
			$modelData = $stmt->fetchAll();
			
			#var_dump(modelData);
			foreach ($modelData as $o) {
				$probablity = $o["probability"];
				$RoomName = $o["RoomName"];
				echo "The following room set up $RoomName is available in $location in $probablity proportion of model runs <br>";
				}
			echo $query;
		}
		
		#echo "lottery: $lottery, time: $time, people: $people, location $location";
		
		
							
		
	}		
	
	catch(PDOException $e) {
		echo "Connection failed: " . $e->getMessage();
		}

?>
</body>
</html>