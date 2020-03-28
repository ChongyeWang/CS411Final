
from flask import Flask
from neo4j import GraphDatabase
import mysql.connector
from mysql.connector import errorcode

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
else:
    print('mysql connected')
    cnx.close()
try:
    uri = "bolt://54.91.232.22:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))
except:
    print('connection failed')
else:
    print('neo4j connected')
app = Flask(__name__)

visit_counter_home = 1

@app.route('/')
def hello_world():
    global visit_counter_home
    str1 =  'Hello, World! You are visitor number '
    str1 += str(visit_counter_home)
    str1 += ' to this page since it\'s been live!'
    visit_counter_home = visit_counter_home + 1
    return str1


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
