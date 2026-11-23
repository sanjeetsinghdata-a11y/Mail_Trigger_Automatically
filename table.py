
import sqlite3
import os

database = "BirthDay.db"

# Check whether database already exists
db_exists = os.path.exists(database)

# Connect to database
conn = sqlite3.connect(database)
cursor = conn.cursor()

if db_exists:
    print("Database already exists.")
else:
    print("New database created.")

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS B_Boys (
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        name VARCHAR(30),
        DOB DATE,
        Email text
    )
""")



print("Table checked and record inserted.")

# Display records
cursor.execute("SELECT * FROM B_Boys")
print(cursor.fetchall())

conn.close()
