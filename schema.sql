drop table if exists entries;
drop table if exists users;

create table entries (
	id integer primary key autoincrement,
	title string not null,
	text string not null
);

create table users (
	id integer primary key autoincrement,
	username string not null,
	salt string not null,
	password string not null
);