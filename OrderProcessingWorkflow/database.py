import sqlite3

DB_NAME = 'order_processing.db'

def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection

