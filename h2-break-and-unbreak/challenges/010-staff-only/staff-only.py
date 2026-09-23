#!/usr/bin/python3
# Copyright 2018-2024 Tero Karvinen http://TeroKarvinen.com
#########################################
# WARNING: Purposefully VULNERABLE APP! #
#########################################

from flask import Flask, render_template, request # sudo apt-get install python3-flask
from flask_sqlalchemy import SQLAlchemy # sudo apt-get install python3-flask-sqlalchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)

@app.route("/", methods=['POST', 'GET'])
def hello():
	if "pin" in request.form:
		pin = str(request.form['pin'])
	else:
		pin = "0"

	sql = "SELECT password FROM pins WHERE pin='"+pin+"';"
	row = ""
	with app.app_context():
		res=db.session.execute(text(sql))
		db.session.commit()
		row = res.fetchone()

	if row is None:
		password="(not found)"
	else:
		password=row[0]
	return render_template('index.html', password=password, pin=pin, sql=sql)

def runSql(sql):
	with app.app_context():
		res=db.session.execute(text(sql))
		db.session.commit()
		return res

def initDb():
	# For simplifying the demo, passwords are also incorrectly stored as plain text. 
	# However, that's not the only thing that's wrong.
	runSql("CREATE TABLE pins (id SERIAL PRIMARY KEY, pin VARCHAR(17), password VARCHAR(20));")
	runSql("INSERT INTO pins(pin, password) VALUES ('321', 'foo');")
	runSql("INSERT INTO pins(pin, password) VALUES ('123', 'Somedude');")
	runSql("INSERT INTO pins(pin, password) VALUES ('11112222333', 'SUPERADMIN%%rootALL-FLAG{Tero-e45f8764675e4463db969473b6d0fcdd}');")
	runSql("INSERT INTO pins(pin, password) VALUES ('321', 'loremipsum');")

if __name__ == "__main__":
	print("WARNING: Purposefully VULNERABLE APP!")
	initDb()
	app.run() # host="0.0.0.0" to serve non-localhost, e.g. from vagrant; debug=True for debug
