import mysql.connector
from dotenv import load_dotenv
import os

# load the environment variables
load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME
)

cursor = connection.cursor()

cursor.execute("SELECT DATABASE();")
print(cursor.fetchone())

cursor.close()
connection.close()