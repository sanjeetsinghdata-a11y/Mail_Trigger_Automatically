
import sqlite3
import os
import time
import datetime as dt
import ssl
import smtplib
from pathlib import Path
from dotenv import load_dotenv
from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import glob



class Birthday_mail_trigger:

    def __init__(self):

        self.base_dir = Path(__file__).resolve().parent

        load_dotenv(self.base_dir / ".gitignore")

        self.sender = "siddharthroy3253@gmail.com"
        self.app_password = os.getenv("app_password")

        self.database = self.base_dir / "BirthDay.db"

        self.scheduler = BackgroundScheduler()

        if not self.app_password:
            raise ValueError(
                "Gmail App Password missing. Check your .env file."
            )

        print("Database:", self.database)
        print("Database type:", type(self.database))

        self.Create_Log_Table()

    ## create table to store all the b boys/girls birthday
    def Create_Store_table(self):
        
        with sqlite3.connect(self.database) as conn:
            cursor=conn.cursor()            
            # Create table
    
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS B_Boys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                DOB TEXT NOT NULL,
                Email TEXT NOT NULL
            )
        """)
            conn.commit()
        print("table created successfully ")
            
            
            
    # Create email history table
    def Create_Log_Table(self):

        with sqlite3.connect(self.database) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Email_Log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id INTEGER NOT NULL,
                    sent_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    UNIQUE(person_id, sent_date),
                    FOREIGN KEY(person_id) REFERENCES B_Boys(id)
                )
            """)

            conn.commit()

        print("Email_Log table created successfully.")

    # Send birthday email
    def Send_Email(self, name, email):

        msg = EmailMessage()

        msg["Subject"] = "Happy Birthday! 🎂"
        msg["From"] = self.sender
        msg["To"] = email

        msg.set_content(f"""
Happy Birthday, {name}! 🎉🎂

Wishing you a wonderful birthday filled with happiness,
success, good health, and unforgettable memories.

Best wishes,
Siddharth
""")

        try:

            context = ssl.create_default_context()

            with smtplib.SMTP(
                "smtp.gmail.com", 587, timeout=30
            ) as server:

                server.ehlo()
                server.starttls(context=context)
                server.ehlo()

                print("Connecting to Gmail...")

                server.login(
                    self.sender,
                    self.app_password.replace(" ", "")
                )

                print("Gmail login successful.")

                server.send_message(msg)

                print(f"Email successfully sent to {email}")

                return True

        except Exception as e:

            print(f"Email sending failed for {email}: {e}")

            return False

    # Check whether email was already sent
    def Already_Sent(self, person_id, today):

        with sqlite3.connect(self.database) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT 1
                FROM Email_Log
                WHERE person_id = ?
                AND sent_date = ?
                AND status = 'SENT'
            """, (person_id, today))

            return cursor.fetchone() is not None

    

    def refresh_data(self):

        with sqlite3.connect(self.database) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, DOB, Email
                FROM B_Boys
            """)

            data = cursor.fetchall()

        print(f"Database refreshed: {len(data)} records loaded.")

        return data

 
            
    # Save email delivery status
    def Save_Email_Log(self, person_id, today, status):

        with sqlite3.connect(self.database) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Email_Log
                (person_id, sent_date, status)
                VALUES (?, ?, ?)

                ON CONFLICT(person_id, sent_date)
                DO UPDATE SET status = excluded.status
            """, (person_id, today, status))

            conn.commit()

    # Check birthdays
    def Msg_trigger(self):

        today = dt.date.today()
        today_str = today.isoformat()

        print(f"\nChecking birthdays: {today_str}")

        try:

            with sqlite3.connect(self.database) as conn:

                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, name, DOB, Email
                    FROM B_Boys
                """)

                rows = cursor.fetchall()

            if not rows:

                print("No people found in the database.")
                return

            for person_id, name, DOB, email in rows:

                try:

                    birthday = dt.date.fromisoformat(DOB)

                except (ValueError, TypeError):

                    print(f"Invalid DOB for {name}: {DOB}")
                    continue

                if (
                    today.month == birthday.month
                    and today.day == birthday.day
                ):

                    print(f"Birthday found: {name}")

                    # Prevent duplicate emails
                    if self.Already_Sent(person_id, today_str):

                        print(f"Already sent to {name}. Skipping.")
                        continue

                    # Send email
                    success = self.Send_Email(name, email)

                    if success:

                        self.Save_Email_Log(
                            person_id,
                            today_str,
                            "SENT"
                        )

                        print(f"Email logged successfully for {name}")

                    else:

                        self.Save_Email_Log(
                            person_id,
                            today_str,
                            "FAILED"
                        )

                else:

                    print(f"Not a birthday: {name}")

        except sqlite3.Error as e:

            print("Database error:", e)

        except Exception as e:

            print("Unexpected error:", e)

    # Start scheduler
    def Start_Scheduler(self):

        # Run immediately once for testing
        self.Msg_trigger()

        self.scheduler.add_job(
            self.Msg_trigger,
            trigger="interval",
            seconds=10,
            id="birthday_email_job",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )

        print("\nBirthday scheduler started.")
        print("Checking birthdays every 10 seconds.")

        self.scheduler.start()

        try:

            while True:
                time.sleep(60)

        except (KeyboardInterrupt, SystemExit):

            self.scheduler.shutdown()
            print("Scheduler stopped.")


if __name__ == "__main__":

    b = Birthday_mail_trigger()
    b.Start_Scheduler()
    
    
