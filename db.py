from neo4j import GraphDatabase
import mysql.connector

try:
    mysql_cnx = mysql.connector.connect(user='admin',
                                        password='adminadmin',
                                        host='database-1.cibdpmq7a2jg.us-east-1.rds.amazonaws.com',
                                        port=3306)
except mysql.connector.Error as err:
    print(err)

try:
    uri = "bolt://3.80.148.94"
    neo4j_driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))
except:
    print('Neo4j connection failed')

mysql_cursor = mysql_cnx.cursor(buffered=True)


def get_user_data(emails):
    """
    Returns an array of tuples (first, last, email) for each inputted email.
    """

    if len(emails) == 0:
        return []

    user_data_query = f"""
        SELECT
            first_name,
            last_name,
            email
        FROM Users.User
        WHERE
            User.email IN ({",".join(("%s",) * len(emails))})
        """

    mysql_cursor.execute(user_data_query, tuple(emails))
    user_data = mysql_cursor.fetchall()

    return user_data
