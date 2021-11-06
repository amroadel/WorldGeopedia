-- Schema WGS
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `WGS`;
USE `WGS` ;

-- -----------------------------------------------------
-- Table `WGS`.`Country`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS Country (
    name                    VARCHAR(255)    NOT NULL,
    calling_code            VARCHAR(255),
    driving_side            CHAR(1),         
    gov_type                CHAR(1),        COMMENT '(P))resident or (M)onarch'
    continent               VARCHAR(255)    NOT NULL,
    population              INT,
    area                    FLOAT,
    water_percentage        FLOAT,           
    gdp_pp                  FLOAT,
    gdp_nominal             FLOAT,
    gini_index              FLOAT,
    hdi                     FLOAT,
    covid_cases             INT,
    vaccines                INT,
    PRIMARY KEY (name)
);

-- -----------------------------------------------------
-- Table `WGS`.`Timezone`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS timezone (
    country_name            VARCHAR(255)    NOT NULL,
    timezone_name           VARCHAR(255)    NOT NULL,
    PRIMARY KEY (country_name, timezone_name),
    FOREIGN KEY (country_name) REFERENCES Country (name)
        ON UPDATE CASCADE  
);

-- -----------------------------------------------------
-- Table `WGS`.`Official_lang`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS official_lang (
    country_name            VARCHAR(255)    NOT NULL,
    language_name           VARCHAR(255)    NOT NULL,
    PRIMARY KEY (country_name, language_name),
    FOREIGN KEY (country_name) REFERENCES Country (name)
        ON UPDATE CASCADE
);

-- -----------------------------------------------------
-- Table `WGS`.`legislature`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS legislature (
    country_name            VARCHAR(255)    NOT NULL,
    legislature_name        VARCHAR(255)    NOT NULL,
    PRIMARY KEY (country_name, legislature_name),
    FOREIGN KEY (country_name) REFERENCES Country (name)
        ON UPDATE CASCADE
);

-- -----------------------------------------------------
-- Table `WGS`.`currency`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS currency (
    country_name            VARCHAR(255)    NOT NULL,
    currency_name           VARCHAR(255)    NOT NULL,
    PRIMARY KEY (country_name, currency_name),
    FOREIGN KEY (country_name) REFERENCES Country (name)
        ON UPDATE CASCADE
);

-- -----------------------------------------------------
-- Table `WGS`.`President`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS President (
    country_name            VARCHAR(255)    NOT NULL,
    name                    VARCHAR(255)    NOT NULL,
    birthdate               DATE,
    political_party         VARCHAR(255),
    assumed_office          DATE            NOT NULL,            
    PRIMARY KEY (country_name, name),
    FOREIGN KEY (country_name) REFERENCES Country (name)
        ON UPDATE CASCADE
);

-- -----------------------------------------------------
-- Table `WGS`.`Capital`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS Capital (
    name                    VARCHAR(255)    NOT NULL,
    country_name            VARCHAR(255)    NOT NULL,
    population              INT,
    governer                VARCHAR(255),
    area                    FLOAT           NOT NULL,
    coordinates             VARCHAR(255),            
    PRIMARY KEY (name),
    FOREIGN KEY (country_name) REFERENCES Country (name)
        ON UPDATE CASCADE
);

-- -----------------------------------------------------
-- Table `WGS`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS User (
    username                VARCHAR(255)    NOT NULL,
    email                   VARCHAR(255)    NOT NULL,
    gender                  CHAR(1),
    birthdate               DATE,
    PRIMARY KEY (username)
);

-- -----------------------------------------------------
-- View `WGS`.`User_age`
-- -----------------------------------------------------
CREATE OR REPLACE VIEW User_age AS 
SELECT TIMESTAMPDIFF(YEAR, U.birthdate, CURDATE()) AS user_age
FROM User U; 

-- -----------------------------------------------------
-- Table `WGS`.`User_review`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS User_review (
    id                      INT				NOT NULL    AUTO_INCREMENT,
    travel_date             DATE            NOT NULL,
    rating                  ENUM('1','2','3','4','5','6','7','8','9','10')  NOT NULL,
    txt_review              VARCHAR(1024),
    username                VARCHAR(255)    NOT NULL,
    country_name            VARCHAR(255)    NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (username) REFERENCES User (username)
        ON UPDATE CASCADE,
    FOREIGN KEY (country_name) REFERENCES Country (name)
        ON UPDATE CASCADE
);