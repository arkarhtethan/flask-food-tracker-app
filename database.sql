create table if not exists log_table (

	id integer primary key autoincrement,

	entry_date date not null

);

create table if not exists food (

	id integer primary key autoincrement,

	name text not null,

	protein integer not null,
	
	carbonhydrates integer not null,

	fat integer not null,
	
	calories integer not null

);

create table if not exists food_date (

	food_id integer not null,

	log_date_id integer not null,

	primary key(food_id, log_date_id)

);

SELECT food.* FROM log_table JOIN food_date ON food_date.log_date_id = log_table.id JOIN food ON food.id = food_date.food_id;

SELECT sum(food.protein) as protein,sum(food.carbonhydrates) as carbonhydrates,sum(food.fat) as fat, sum(food.calories) as calories  FROM log_table JOIN food_date ON food_date.log_date_id = log_table.id JOIN food ON food.id = food_date.food_id GROUP BY log_table.entry_date;

