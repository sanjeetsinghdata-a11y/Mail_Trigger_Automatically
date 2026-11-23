
import sqlite3
import os
import time
import datetime as dt
import ssl
import smtplib
from dotenv import load_dotenv


from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler


class Birthday_mail_trigger:

    def __init__(self):

        self.sender = "siddharthroy3253@gmail.com"
        self.receiver = "sanjeet.singh.data@gmail.com" 
        
        load_dotenv()

        self.app_password = os.getenv("app_password")       

        self.database = "BirthDay.db"
        self.scheduler = BackgroundScheduler()


    # Send birthday email
    def Send_Email(self, name):

        msg = EmailMessage()

        msg["Subject"] = "Happy Birthday! 🎂"
        msg["From"] = self.sender
        msg["To"] = self.receiver
            
            
        msg.set_content(f"""
        Happy Birthday, {name}! 🎉🎂

        Wishing you th a wonderful birthday filled with happiness,
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

                print("SMTP connection established")

                server.login(
                    self.sender,
                    self.app_password.replace(" ", "")
                )

                print("Gmail login successful")

                server.send_message(msg)

                print(f"Birthday email sent to {name}!")

        except Exception as e:
            print("Email error:", e)

    # Check birthdays
    def Msg_trigger(self):

        today = dt.date.today()

        with sqlite3.connect(self.database) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, DOB,Email
                FROM B_Boys
            """)

            rows = cursor.fetchall()

        for person_id, name, DOB,Email in rows:

            birthday = dt.date.fromisoformat(DOB)

            if (
                today.month == birthday.month
                and today.day == birthday.day
            ):

                print(f"Birthday found: {name}")

                self.Send_Email(Email)

    
    def Start_Scheduler(self):

        self.scheduler.add_job(
        self.Msg_trigger,
         trigger="cron",
        hour=9,
        minute=0,
        id="birthday_email_job",
        replace_existing=True
    )

        self.scheduler.start()

        print("Birthday scheduler started!")
        print("Daily check scheduled at 9:00 AM.")

        
        try:
            while True:
                time.sleep(60)

        except (KeyboardInterrupt, SystemExit):

            self.scheduler.shutdown()
            print("Scheduler stopped.")


  
b = Birthday_mail_trigger()


b.Start_Scheduler()

 
    
