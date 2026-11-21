
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
        id INTEGER PRIMARY KEY,
        name VARCHAR(30),
        DOB DATE,
        Email text
    )
""")



# Insert sample record only if it doesn't already exist
cursor.execute("""
    INSERT OR IGNORE INTO B_Boys (id, name, DOB,Email)
    VALUES (?, ?, ?,?)
""", (1, "Singh", "2026-11-22"))


cursor.execute("""
               update B_Boys
               set Email='Sanjeet.singh.data@gmail.com'
               where id=1
               """)
print("table has been updated")
conn.commit()

print("Table checked and record inserted.")

# Display records
cursor.execute("SELECT * FROM B_Boys")
print(cursor.fetchall())

conn.close()
