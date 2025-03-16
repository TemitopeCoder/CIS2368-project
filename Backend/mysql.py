import pymysql
import pymysql.cursors
import mycred
from pymysql import Error


creds = mycred.CRED()
conString = creds.constring
username = creds.username
password = creds.password
dbname = creds.dbname

def create_connection():
    connection = None
    try:
        connection = pymysql.connect(
            host=conString,
            user=username,
            password=password,
            db=dbname) 
        
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_read_query(connection, query, params=None):
    cursor = connection.cursor(pymysql.cursors.DictCursor)  # Use dictionary cursor
    result = None
    try:
        if params:
            cursor.execute(query, params)  # Use parameterized query
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except pymysql.Error as e:
        print(f"The error '{e}' occurred")

def execute_query(connection, query, values=None):
    cursor = connection.cursor()
    try:
        if values:
            cursor.execute(query, values) 
        else:
            cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

    finally:
        cursor.close()
         
