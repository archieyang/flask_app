import sqlite3, hashlib, time
from flask import Flask, g, render_template, request, redirect, url_for, flash, session
from contextlib import closing

app = Flask(__name__)
app.config.from_object('config')

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
def init_db():
	with closing (connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()


@app.route('/')
def show_entries():
	cur = g.db.execute('select title, text from entries order by id desc')
	entries = [dict(title = row[0], text = row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries = entries)

@app.route('/add', methods = ['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into entries ( title, text) values (?, ?)',[request.form['title'], request.form['text']])
	g.db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

def secure_hash(salt, password):
	return hashlib.sha224(str(salt) + '--' + password).hexdigest()

@app.route('/sign_up', methods = ['POST', 'GET'])
def sign_up():
	if request.method == 'POST':
		msg = None
		if request.form['username'] is None:
			msg = 'Please input username !'

		
		if request.form['password'] is None:
			msg = 'Please input password ! '

		if msg is None:
			msg = 'New user added!'
			salt = (int)(time.time())

			secured_pwd = secure_hash(salt, request.form['password'])

			g.db.execute('insert into users ( username, salt, password ) values (?, ?, ?)', [request.form['username'], salt, secured_pwd])
			g.db.commit()

		flash(msg)
		return redirect(url_for('show_entries'))
	return render_template('sign_up.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		cur = g.db.execute('select salt, password from users where username=?', [request.form['username']])
		user_dict = cur.fetchall()
		print user_dict
		if len(user_dict) != 0:
			for row in user_dict:
				salt = row[0]
				password = row[1]

			if password == secure_hash(salt, request.form['password']):	
				session['logged_in'] = True
				flash('Logged in !!!')
				return redirect(url_for('show_entries'))
	flash('No user or wrong password...')
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('Logged out !')
	return redirect(url_for('show_entries'))	

@app.route('/users')
def show_users():
	cur = g.db.execute('select username, password from users order by username')
	users = [dict(username = row[0], password = row[1]) for row in cur.fetchall()]
	return render_template('show_users.html', users = users)

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=80)
	app.run()


