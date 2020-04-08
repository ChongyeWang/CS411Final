from flask import Flask, render_template, flash, request, url_for
from neo4j import GraphDatabase
import mysql.connector
from mysql.connector import errorcode
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import register
from register import register_api
import pandas as pd
#mysql -h database-1.cibdpmq7a2jg.us-east-1.rds.amazonaws.com -u admin -p

try:
    cnx = mysql.connector.connect(user='admin',
                                  password='adminadmin',
                                  host='database-1.cibdpmq7a2jg.us-east-1.rds.amazonaws.com',
                                  port= 3306)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    else:
        print(err)

try:
    uri = "bolt://54.91.232.22:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))
except:
    print('connection failed')
else:
    print('neo4j connected')


app = Flask(__name__)

app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.register_blueprint(register_api)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
