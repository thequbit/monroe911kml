create database monroe911;

create table tweets ( tweetid int not null auto_increment primary key, tweettext text not null, lat int not null, lng int not null, tweetdate date not null, tweettime time not null);


