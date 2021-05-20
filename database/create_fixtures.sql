create table if not exists followers_history
(
	id serial not null
		constraint followers_history_pk
			primary key,
	insert_date date,
	follower_name text,
	follower_screen_name text,
	follower_id text,
	number integer
);

create table if not exists followers_gained
(
	id serial not null
		constraint followers_gained_pk
			primary key,
	insert_date date,
	follower_id text,
	follower_name text,
	follower_screen_name text
);

create table if not exists followers_lost
(
	id serial not null
		constraint followers_lost_pk
			primary key,
	insert_date date,
	follower_id text,
	follower_name text,
	follower_screen_name text
);