
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
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS B_Boys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        DOB TEXT NOT NULL,
        Email TEXT NOT NULL
    )
""")
    
    
    
    print("table has been established ")
    conn.commit()

except  sqlite3.Error as e:
    print(f"{e}")
    


# Display records
cursor.execute("SELECT * FROM B_Boys")
print(cursor.fetchall())

conn.close()
