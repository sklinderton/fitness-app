CREATE DATABASE fitness_app;
USE fitness_app;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sex ENUM('M', 'F', 'Other') NOT NULL,
    weight FLOAT NOT NULL,
    height FLOAT NOT NULL,
    age INT NOT NULL
);

CREATE TABLE raw_weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    raw_data TEXT NOT NULL,
    query_date DATETIME NOT NULL
);

CREATE TABLE cleaned_weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    temperature FLOAT NOT NULL,
    humidity INT NOT NULL,
    wind_speed FLOAT NOT NULL,
    pressure INT NOT NULL,
    condition VARCHAR(100) NOT NULL,
    uv FLOAT NOT NULL,
    chance_of_rain INT NOT NULL,
    query_date DATETIME NOT NULL
);

CREATE TABLE queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    city VARCHAR(100) NOT NULL,
    activity VARCHAR(100) NOT NULL,
    recommendation TEXT NOT NULL,
    query_date DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);