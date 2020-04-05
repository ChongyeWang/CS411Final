from flask import Flask, render_template, flash, request
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
# else:
#     print('mysql connected')
#     cnx.close()
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

visit_counter_home = 1


@app.route('/', methods=['GET', 'POST'])
def hello_world():


    sql = """
    SELECT * FROM Users.User
    """
    a = pd.read_sql(sql, con=cnx)

    print(a)

    global visit_counter_home
    str1 =  'Hello, World! You are visitor number '
    str1 += str(visit_counter_home)
    str1 += ' to this page since it\'s been live!'
    visit_counter_home = visit_counter_home + 1
    return str1




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
