import sqlite3
from flask import Flask
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
def hello_world():
	return 'Hello World'
if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=80)
	app.run()