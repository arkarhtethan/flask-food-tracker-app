from flask import Flask, render_template, g, request
import sqlite3
from datetime import datetime

app = Flask(__name__)


def connect_db():

    sql = sqlite3.connect('./food_log.db')

    sql.row_factory = sqlite3.Row

    return sql

def get_db():

    if not hasattr(g, 'sqlite3'):

        g.sqlite_db = connect_db()

    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):

    if hasattr(g, 'sqlite3'):

        g.sqlite_db.close()

@app.route('/', methods=['GET','POST'])
def home():

	db = get_db()

	if request.method == "POST":

		date = request.form['date']

		dt = datetime.strptime(date, '%Y-%m-%d')
		
		db_date = datetime.strftime(dt, '%Y%m%d')

		db.execute('INSERT INTO log_table(entry_date) values(?);',[db_date])

		db.commit()

	cur = db.execute('''
		
		SELECT log_table.entry_date,sum(food.protein) as protein,sum(food.carbonhydrates) as carbonhydrates,sum(food.fat) as fat, sum(food.calories) as calories 
		FROM log_table 
		LEFT JOIN food_date ON food_date.log_date_id = log_table.id 
		LEFT JOIN food ON food.id = food_date.food_id 
		GROUP BY log_table.entry_date 
		ORDER BY log_table.entry_date;

		''')

	results = cur.fetchall()

	pretty_date = []

	print(results)

	for i in results:

		single_date = {}

		single_date['entry_date'] = i['entry_date']
		
		d = datetime.strptime(str(i['entry_date']),'%Y%m%d')
		
		single_date['pretty_date'] = datetime.strftime(d,"%B %d, %Y")

		single_date['protein'] = i['protein']
		
		single_date['carbonhydrates'] = i['carbonhydrates']

		single_date['fat'] = i['fat']

		single_date['calories'] = i['calories']

		pretty_date.append(single_date)

	return render_template('home.html', results=pretty_date)

@app.route('/view/<date>', methods=['GET','POST'])
def view(date):

	db = get_db()

	cur = db.execute('SELECT id,entry_date from log_table where entry_date = ?',[date])

	date_result = cur.fetchone()

	if request.method == "POST":

		food = request.form['food']

		db.execute('INSERT INTO food_date(food_id,log_date_id) values(?,?)',[food,date_result['id']])

		db.commit()


	d = datetime.strptime(str(date_result['entry_date']),'%Y%m%d')

	pretty_date = datetime.strftime(d, '%B %d, %Y')

	food_cur = db.execute("SELECT id,name FROM food;")

	foods = food_cur.fetchall()

	foods_per_day_cur = db.execute('''SELECT food.* 
		FROM log_table 
		JOIN food_date ON food_date.log_date_id = log_table.id 
		JOIN food ON food.id = food_date.food_id 
		WHERE log_table.entry_date = ?;
		''',[date])

	foods_per_day_results = foods_per_day_cur.fetchall()

	totals = {}
	totals['protein']  = 0
	totals['carbonhydrates'] = 0
	totals['fat']  = 0
	totals['calories'] = 0

	for food in foods_per_day_results:

		totals['protein'] += food['protein']
		totals['carbonhydrates'] += food['carbonhydrates']
		totals['fat'] += food['fat']
		totals['calories'] += food['calories']

	context = {
		'entry_date':date_result['entry_date'],
		'pretty_date':pretty_date, 
		'foods':foods, 
		'foods_per_day_results':foods_per_day_results, 
		'totals':totals
	}

	return render_template('day.html', **context)

@app.route('/food', methods=['GET','POST'])
def food():

	db = get_db()	
	
	if request.method == "POST":

		name = request.form['name']

		protein = int(request.form['protein'])

		carbonhydrates = int(request.form['carbohydrates'])

		fat = int(request.form['fat'])
		
		calories = protein * 4 + fat * 4 + carbonhydrates * 9

		db.execute('insert into food(name, protein, carbonhydrates,fat,calories) values(?,?,?,?,?)',[name,protein,carbonhydrates,fat,calories])

		db.commit()

	cur = db.execute("SELECT * FROM food;")

	foods = cur.fetchall()

	return render_template('add_food.html',foods=foods)