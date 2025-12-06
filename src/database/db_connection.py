import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'db'),
                user=os.getenv('MYSQL_USER', 'user'),
                password=os.getenv('MYSQL_PASSWORD', 'password'),
                database=os.getenv('MYSQL_DATABASE', 'capstone_db'),
                allow_local_infile=True  # Enable LOAD DATA LOCAL INFILE
            )
            print("Successfully connected to the database")
        except Error as e:
            print(f"Error connecting to MySQL Database: {e}")

    def get_connection(self):
        return self.connection

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")
