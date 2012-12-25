create database monroe911;

grant usage on _database_.* to _username_ identified by _passowrd_;

grant all privileges on _database_.* to _username_ ;

create table tweets ( tweetid int not null auto_increment primary key, tweettext text not null, lat int not null, lng int not null, tweetdate date not null, tweettime time not null);


