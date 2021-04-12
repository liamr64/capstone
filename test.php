<html>

	<head>
		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
			<div class = "jumbotron text-center">
				<h1>Probabilites of room availability</h1>
				
			</div>
			
	
	</head>

<body>
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
		$lotterySet = strcmp($lottery, "Enter Lottery...") != 0;
		$timeSet = strcmp($time, "") != 0;
		$locationSet = strcmp($location, "Location...") != 0;
		$peopleSet = strcmp($people, "Total Number of People") != 0;
		echo $locationSet;
		
		
		if ($lotterySet and $timeSet and $locationSet and $peopleSet) {
			$query = "SELECT ModelData.probability, Room.RoomName FROM ModelData INNER JOIN Room on ModelData.Room_id INNER JOIN Residence_Hall ON Room.Residence_Hall_idResidence_Hall
					 WHERE ModelData.Time = \"$time\" and Residence_Hall.ResName = \"$location\" and Room.Occupancy = $people and Residence_Hall_idResidence_Hall = idResidence_Hall and id = Room_id";
			$stmt = $conn->prepare($query);
			$stmt->execute();
			// set the resulting array to associative
			$result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
			$modelData = $stmt->fetchAll();
			
			#var_dump(modelData);
			foreach ($modelData as $o) {
				$percentage = (float)$o["probability"] * 100;
				$RoomName = $o["RoomName"];
				echo "<center> The room set up $RoomName is available in $location in $percentage percent of model runs </center> <br>";
				}
			#echo $query;
		}
		else if ($lotterySet and $timeSet and $locationSet) {
			$query = "SELECT ModelData.probability, Room.RoomName FROM ModelData INNER JOIN Room on ModelData.Room_id INNER JOIN Residence_Hall ON Room.Residence_Hall_idResidence_Hall
					 WHERE ModelData.Time = \"$time\" and Residence_Hall.ResName = \"$location\" and Residence_Hall_idResidence_Hall = idResidence_Hall and id = Room_id";
			$stmt = $conn->prepare($query);
			$stmt->execute();
			// set the resulting array to associative
			$result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
			$modelData = $stmt->fetchAll();
			
			#var_dump(modelData);
			foreach ($modelData as $o) {
				$percentage = (float)$o["probability"] * 100;
				$RoomName = $o["RoomName"];
				echo "<center> The room set up $RoomName is available in $location in $percentage percent of model runs </center> <br>";
				}
			#echo $query;
		}
		else if ($lotterySet and $timeSet and $peopleSet) {
			$query = "SELECT ModelData.probability, Room.RoomName, Residence_Hall.ResName FROM ModelData INNER JOIN Room on ModelData.Room_id INNER JOIN Residence_Hall ON Room.Residence_Hall_idResidence_Hall
					 WHERE ModelData.Time = \"$time\" and Room.Occupancy = $people and Residence_Hall_idResidence_Hall = idResidence_Hall and id = Room_id";
			$stmt = $conn->prepare($query);
			$stmt->execute();
			// set the resulting array to associative
			$result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
			$modelData = $stmt->fetchAll();
			
			#var_dump(modelData);
			foreach ($modelData as $o) {
				$percentage = (float)$o["probability"] * 100;
				$RoomName = $o["RoomName"];
				$location = $o["ResName"];
				echo "<center> The room set up $RoomName is available in $location in $percentage percent of model runs </center> <br>";
				}
			echo "1";
		}
		else if ($lotterySet and $timeSet) {
			$query = "SELECT ModelData.probability, Room.RoomName, Residence_Hall.ResName FROM ModelData INNER JOIN Room on ModelData.Room_id INNER JOIN Residence_Hall ON Room.Residence_Hall_idResidence_Hall
					 WHERE ModelData.Time = \"$time\" and Residence_Hall_idResidence_Hall = idResidence_Hall and id = Room_id";
			$stmt = $conn->prepare($query);
			$stmt->execute();
			// set the resulting array to associative
			$result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
			$modelData = $stmt->fetchAll();
			
			#var_dump(modelData);
			foreach ($modelData as $o) {
				$percentage = (float)$o["probability"] * 100;
				$RoomName = $o["RoomName"];
				$location = $o["ResName"];
				echo "<center> The room set up $RoomName is available in $location in $percentage percent of model runs </center> <br>";
				}
		}
		else {
			echo "<center>A time is required on order to use this tool</center>";
			$noTime = True;
		}
		if (sizeof($modelData)== 0 and !$noTime){
			echo "<center>There is no model data for the entered time </center>";
		}
		
		#echo "lottery: $lottery, time: $time, people: $people, location $location";
		
		
							
		
	}		
	
	catch(PDOException $e) {
		echo "Connection failed: " . $e->getMessage();
		}

?>
</body>
</html>