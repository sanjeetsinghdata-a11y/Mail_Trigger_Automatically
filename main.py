
import sqlite3
import os
import datetime as dt
import ssl
import smtplib

from pathlib import Path
from dotenv import load_dotenv
from email.message import EmailMessage


class Birthday_mail_trigger:

    def __init__(self):

        # Project configuration
        self.base_dir = Path(__file__).resolve().parent

        # Load environment variables
        load_dotenv(self.base_dir / ".gitignore")

        self.sender = "siddharthroy3253@gmail.com"
        self.app_password = os.getenv("app_password")

        self.database = self.base_dir / "BirthDay.db"

        if not self.app_password:
            raise ValueError(
                "Gmail App Password missing. Check your environment file."
            )

        print("Database:", self.database)

        # Create email history table automatically
        self.Create_Log_Table()

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
    
    
    
    def To_Boss(self,Name,Boss):
        
        msg=EmailMessage()
        msg['subject']='Daily Birthday Update – No Birthdays Today'
        msg['from']=self.sender
        msg['to']=Boss
        
        msg.set_content(
                f"""
            Dear Sir {Name},

            Good morning!

            Just a quick update: today's birthday check has been completed successfully,
            and there are no employee birthdays scheduled for today.
            No birthday wishes or notifications are required at this time.
            The system will continue checking automatically and will notify you whenever an
            employee's birthday comes up.
            Have a wonderful day!

            Best regards,
            HR Team
            Birthday Automation System
            """
            )
        context=ssl.create_default_context()
        try:
        
            with smtplib.SMTP('smtp.gmail.com',587,timeout=30) as server:
                
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.sender,self.app_password)
                print("connection have been established successfully")
                
                server.send_message(msg)
                print("msg has been sent to the boss")
                
        except Exception as e:
            print(f"error {e}")
        except smtplib._SendErrs as e:
            print(f"error {e}")
            
    
    #  send to fail msg to the boss 
    def Fail_Email(self,Name,Boss,BBoys):
        
        msg=EmailMessage()
        msg['Subject']='Failed Emailed to Send '
        msg['from']=self.sender
        msg['to']=Boss
        
        failed_details = "\n".join(
        f"Record {i}: {' | '.join(map(str, record))}"
        for i, record in enumerate(BBoys, start=1)
        )

        
        msg.set_content(f"""
                        Dear Sir {Name},

                        Good morning!

                        I would like to inform you that the Birthday Automation System encountered an 
                        issue while attempting to send the birthday notification email.
                        Unfortunately, the email could not be delivered successfully due to a sending error.
                        **Status:** Email Delivery Failed
                        The system has recorded the failure, and the issue requires attention
                        to ensure that no important birthday notifications are missed.
                        I apologize for the inconvenience and will ensure that the email 
                        delivery process is checked.
                        
                        
                        failed to sent birthday wish {failed_details}
                        
                        Best regards,  
                        HR Team  
                        Birthday Automation System
                        
        """)
        context=ssl.create_default_context()
        try:
            with smtplib.SMTP('smtp.gmail.com',587,timeout=30) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.sender,self.app_password)
                print("connection have been successfully  established")
                
                server.send_message(msg)
                print("msg  has been sent to the boss")
        except smtplib._SendErrs as e:
            print(f"error {e}")
        except Exception as e:
            
            print(f"got an error {e}")
        
    
    #  fetching the failed email msg BBOys/girl's information to report the boss about
    def get_fail_email(self,today_str):
        
        
        query = """
        SELECT *
        FROM Email_log
        WHERE today = ?
        AND UPPER(status) = 'FAILED'
            """
        try:
            with sqlite3.connect(self.database) as conn:
                
                cursor=conn.cursor()
                cursor.execute(query,(today_str,))
                
                failed=cursor.fetchall()
                print("failed record has been gathered")
        except sqlite3.Error as e:
            print(f" failed to get  all  the failed email {e}")
        except Exception as e:
            print(f"this is error  getting from the fail email function ,the error is {e}")
           

        return failed
    
    #  update boss table 
    
    def update_boss_table(self):
        
        with sqlite3.connect(self.database) as conn:
            cursor=conn.cursor()
            
            cursor.execute(
                """create table if not exists update_boss(
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Date CURRENT_TIMESTAMP ,
                    status TEXT 
                )"""
            )
            
        conn.commit()
    
    def update_boss_save_status(self,today_str,status):
        try:
            with sqlite3.connect(self.database) as conn:
                
                cursor=conn.cursor()
                cursor.execute("insert into update_boss (Date,status) values(?,?)",(today_str,status))
                conn.commit()
                
            return True
        except sqlite3.Error as e:
            print(f" error got in update boss save status {e} ")
        
        except Exception as e:
            print(f"error from update boss save status {e}")
            return False
    
     
    # sending email msg to the BBoys'Girls Birthday's are stored in Database
    
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

                    # Validate email
                    if not email:

                        print(f"Email address missing for {name}.")

                        self.Save_Email_Log(
                            person_id,
                            today_str,
                            "FAILED"
                        )

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
                        # getting only those emails  are filed to sent
                        failed=self.Send_Email(name,email)
                        
                        if failed:
                            self.Fail_Email('siddharth rroy','siddharthroy3253@gmail.com',BBoys=failed)
                        else:
                            print("failed to updated boss about failed email operation for the birthday schdule for today")
                       
                else:
                    
                    print(f"Not a birthday: {name}")
                    self.update_boss_table()
                                 
                    
                    with sqlite3.connect(self.database) as conn:
                        cursor = conn.cursor()

                        cursor.execute("""
                            SELECT 1
                            FROM update_boss
                            WHERE DATE(Date) = DATE('now', 'localtime')
                            AND status = 'UPDATED'
                            LIMIT 1
                        """)

                        already_sent = cursor.fetchone()

                        if not already_sent:
                            sent = self.To_Boss(
                                'Siddhart Rroy',
                                'siddharthroy3253@gmail.com'
                            )

                            if sent:
                                cursor.execute("""
                                    INSERT INTO update_boss (status)
                                    VALUES (?)
                                """, ('UPDATED',))

                                conn.commit()
                                print("Boss notified successfully")

                            else:
                                print("Failed to notify boss")

                        # else:
                        #     print("Boss already notified today. Skipping email.") 
                    # self.To_Boss('Siddharth Singhania',Boss='siddharthroy3253@gmail.com')
        except sqlite3.Error as e:

            print("Database error:", e)
            raise

        except Exception as e:

            print("Unexpected error:", e)
            raise

    # Start birthday automation
    # Windows Task Scheduler controls execution time

    def Start_Scheduler(self):

        print("\nBirthday email automation started.")

        try:

            self.Msg_trigger()

            print("\nBirthday check completed successfully.")

        except Exception as e:

            print("\nBirthday automation failed:", e)

            raise

        finally:

            print("\nProgram execution finished.")
            print("Python process will now exit.")


if __name__ == "__main__":

    try:

        b = Birthday_mail_trigger()

        b.Start_Scheduler()

    except Exception as e:

        print("Application error:", e)

        raise SystemExit(1)


