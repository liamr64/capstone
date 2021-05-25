-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema Capstone
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema Capstone
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `Capstone` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `Capstone` ;

-- -----------------------------------------------------
-- Table `Capstone`.`Lottery`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Capstone`.`Lottery` (
  `idLottery` INT NOT NULL AUTO_INCREMENT,
  `LotteryName` VARCHAR(45) NOT NULL,
  `University` VARCHAR(45) NULL DEFAULT NULL,
  `StartTime` VARCHAR(45) NOT NULL,
  `timeBetween` INT NOT NULL,
  `numSlots` INT NOT NULL,
  `numTimes` INT NOT NULL,
  PRIMARY KEY (`idLottery`),
  UNIQUE INDEX `LotteryName_UNIQUE` (`LotteryName` ASC, `University` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 120
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `Capstone`.`Residence_Hall`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Capstone`.`Residence_Hall` (
  `idResidence_Hall` INT NOT NULL AUTO_INCREMENT,
  `ResName` VARCHAR(45) NOT NULL,
  `Lottery_idLottery` INT NOT NULL,
  PRIMARY KEY (`idResidence_Hall`),
  UNIQUE INDEX `oneHallPerLot` (`ResName` ASC, `Lottery_idLottery` ASC) VISIBLE,
  INDEX `lotteryId_idx` (`Lottery_idLottery` ASC) VISIBLE,
  CONSTRAINT `lotteryId`
    FOREIGN KEY (`Lottery_idLottery`)
    REFERENCES `Capstone`.`Lottery` (`idLottery`))
ENGINE = InnoDB
AUTO_INCREMENT = 820
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `Capstone`.`Room`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Capstone`.`Room` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `RoomName` VARCHAR(45) NOT NULL,
  `Occupancy` INT NOT NULL,
  `numAvailable` INT NOT NULL,
  `Residence_Hall_idResidence_Hall` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `aRoom` (`Occupancy` ASC, `RoomName` ASC, `Residence_Hall_idResidence_Hall` ASC) VISIBLE,
  INDEX `fromResHall_idx` (`Residence_Hall_idResidence_Hall` ASC) VISIBLE,
  CONSTRAINT `fromResHall`
    FOREIGN KEY (`Residence_Hall_idResidence_Hall`)
    REFERENCES `Capstone`.`Residence_Hall` (`idResidence_Hall`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1903
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `Capstone`.`ModelData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Capstone`.`ModelData` (
  `modelDataId` INT NOT NULL AUTO_INCREMENT,
  `Room_id` INT NOT NULL,
  `Time` TIME NOT NULL,
  `probability` DECIMAL(11,10) NOT NULL,
  PRIMARY KEY (`modelDataId`),
  UNIQUE INDEX `forUpdate` (`Room_id` ASC, `Time` ASC) VISIBLE,
  UNIQUE INDEX `forUpdateModelData` (`Room_id` ASC, `Time` ASC) INVISIBLE,
  CONSTRAINT `fk_Model Data_Room1`
    FOREIGN KEY (`Room_id`)
    REFERENCES `Capstone`.`Room` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 30913
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `Capstone`.`SampleData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Capstone`.`SampleData` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Room_id` INT NOT NULL,
  `Year` YEAR NOT NULL,
  `Time` TIME NOT NULL,
  `Slot` VARCHAR(45) NOT NULL,
  `updateTime` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `safeUpdate` (`Room_id` ASC, `Year` ASC, `Time` ASC, `Slot` ASC) VISIBLE,
  INDEX `fk_SampleData_Room1_idx` (`Room_id` ASC) VISIBLE,
  CONSTRAINT `fk_SampleData_Room1`
    FOREIGN KEY (`Room_id`)
    REFERENCES `Capstone`.`Room` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 5102
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
