from neo4j import GraphDatabase
import mysql.connector

try:
    mysql_cnx = mysql.connector.connect(user='admin',
                                  password='adminadmin',
                                  host='database-1.cibdpmq7a2jg.us-east-1.rds.amazonaws.com',
                                  port= 3306)
except mysql.connector.Error as err:
    print(err)

try:
    uri = "bolt://54.91.232.22:7687"
    neo4j_driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))
except:
    print('Neo4j connection failed')

mysql_cursor = mysql_cnx.cursor(buffered = True)