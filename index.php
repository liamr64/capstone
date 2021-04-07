<!DOCTYPE html>
<html>

	<head>
		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
			<div class = "jumbotron text-center">
				<h1>Predict the Lottery</h1>
				
			</div>
			
	
	</head>
	
	<?php
		$lotterySet = (isset($_GET["lottery"]) and strcmp($_GET["lottery"], "Enter Lottery...") !== 0);
		$timeSet = isset($_GET["time"]);
		if ($lotterySet){
			echo "<form  action = \"/capstone/test.php\" style=\"margin-left:2.5em\">";
		} else {
			echo "<form  action = \"/capstone/index.php\" style=\"margin-left:2.5em\">";
		}
	?>
	
	
		<input class="btn btn-primary" type="reset" value="Reset">

		<div class="form-group row" >
			<div class = "col-1.5">
				<body> <br> &nbsp; &nbsp; I am participating in &nbsp;</body>
			</div>
			
			<div class = "col-0.5">
				<br>
				<select class="combo" name = "lottery" <?php if ($lotterySet){echo "disabled = \"disabled\"";} ?>>
					<?php
						$servername = "database-1.ceb0m91rauea.us-east-1.rds.amazonaws.com";
						$username = "admin";
						$dbname = "Capstone";
						$password = "1387194#";

						try {
							$conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
							// set the PDO error mode to exception
							$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
							$stmt = $conn->prepare("SELECT LotteryName FROM Lottery");
							$stmt->execute();
							if ($lotterySet){
								$pulled = $_GET["lottery"];
								echo "<option><i>$pulled</i></option>";
							}
							else {
								echo "<option><i>Enter Lottery...</i></option>";
							}
							
							
							// set the resulting array to associative
							$result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
							$lotteries = $stmt->fetchAll();
		
							
							foreach ($lotteries as $l) {
									$lotName = $l["LotteryName"];
									echo "<option><i>$lotName</i></option>";
								}
							}		
						catch(PDOException $e) {
							echo "Connection failed: " . $e->getMessage();
							}
						?>
				
				
				</select>
			</div>
			
			
			
			<div class = "col-1.5">
				<p><br> &nbsp; and I have a time slot of  &nbsp;</p>
			</div>
			<input type="time" class="col-0" size="4" name = "time" <?php if (!$lotterySet){echo "disabled = \"disabled\"";} ?>/>
			
			<div class = "col-1.5">
				<p> <br>&nbsp; and want to live in a suite with at total occupancy of &nbsp; </p>
			</div>
			<div class = "col-0.5">
			<br>
			
				<select class="combo" name = "people" <?php if (!$lotterySet){echo "disabled = \"disabled\"";} ?>>
				<?php
						$servername = "database-1.ceb0m91rauea.us-east-1.rds.amazonaws.com";
						$username = "admin";
						$dbname = "Capstone";
						$password = "1387194#";

						try {
							$tempLottery = $_GET["lottery"];
							$conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
							// set the PDO error mode to exception
							$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
							$query = "SELECT distinct Room.Occupancy FROM Room
							inner join Residence_Hall on Room.Residence_Hall_idResidence_Hall = idResidence_Hall
							inner join Lottery on Residence_Hall.Lottery_idLottery = idLottery
							where LotteryName = \"$tempLottery\"";
							$stmt = $conn->prepare($query);
							
							$stmt->execute();
							echo "<option><i>Total Number of People</i></option>";
							// set the resulting array to associative
							$result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
							$occupancy = $stmt->fetchAll();
							
							$count = 0;
							$occupancies = array();
							foreach ($occupancy as $o) {
									$occupancies[$count] = $o["Occupancy"];
									$count = $count + 1;
								}
							sort($occupancies);
							foreach ($occupancies as $o) {
									echo "<option><i>$o</i></option>";
								}
							}		
						catch(PDOException $e) {
							echo "Connection failed: " . $e->getMessage();
							}
						?>
				</select>
			</div>
			
			<div class = "col-1.5">
				<p><br>&nbsp;and is located at &nbsp;</p>
			</div>
			
			<div class = "col-0.5">
			<br>
				<select class="combo"  name = "location" <?php if (!$lotterySet){echo "disabled = \"disabled\"";} ?>>
				<option><i>Location...</i></option>
				<?php
						$servername = "database-1.ceb0m91rauea.us-east-1.rds.amazonaws.com";
						$username = "admin";
						$dbname = "Capstone";
						$password = "1387194#";

						try {
							$conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
							$query = "SELECT distinct Residence_Hall.ResName FROM Residence_Hall
							inner join Lottery on Residence_Hall.Lottery_idLottery = idLottery
							where LotteryName = \"$tempLottery\"";
							// set the PDO error mode to exception
							$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
							$stmt = $conn->prepare($query);
							$stmt->execute();
							// set the resulting array to associative
							$result = $stmt->setFetchMode(PDO::FETCH_ASSOC);
							$location = $stmt->fetchAll();
							
							$count = 0;
							$locations = array();
							foreach ($location as $l) {
									$locations[$count] = $l["ResName"];
									$count = $count + 1;
								}
							sort($locations);
							foreach ($locations as $l) {
									echo "<option><i>$l</i></option>";
								}
							}		
						catch(PDOException $e) {
							echo "Connection failed: " . $e->getMessage();
							}
						?>
				</select>
			</div>
			
			
		</div>
		

		
		<body style="margin-left:2.5em"><b> This website is designed to help predict the housing lottery for the university lotteries and give users a probablistic estimate of what housing will be available at a given time slot.  
		In order to use it, you need to know which lottery you are participating it and what time slot you have.  You can then narrow your results by occupancy, location or both.  
		Currently the site works for the following universites:<br>
		CNU (Sophmore Housing Lottery)<br>
		CNU (Upperclassman Housing Lottery)</b><br><br>
		
		</body>
		
		
		<input class="btn btn-primary" type="submit" <?php if (!$lotterySet){echo "value = \"Next\"";} else{echo "value = \"Submit\"";} ?>>
		</form>
		
	
</html>