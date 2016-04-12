CREATE TABLE `game` (
  `game_id` varchar(255),
  `failure_times` int DEFAULT NULL,
  `finished` boolean DEFAULT 0,
  `guess_word` varchar(255) DEFAULT NULL,
  `level` char(1) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `word` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`game_id`),
  KEY (`user_id`)
);