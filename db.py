""" 
    In this file, a database will be created using 
    the sqlite3 library. The database will consist of the following three tables:
    - User Data
    - Habit Data
    - Counter Data
    The habit and the counter tables will make use of foreign keys
    to reference data of the other two respective tables.
    Furthermore, there will be various functions that involve the database.
"""

import sqlite3
import logging
import os
from datetime import datetime

#Log configuration for error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Central variable for database connection
db_connection = None  

#The database "main_db.db" will be created
def get_db(name="main_db.db"):
    """Function to create and return a database connection"""
    global db_connection
    if db_connection is None:
        try:
            if not os.path.exists(name):
                logging.info(f"Database '{name}' not found. Creating a new one.")
            db_connection = sqlite3.connect(name)
            logging.info(f"Database '{name}' connection was successful")
        except sqlite3.Error as e:
            logging.error(f"The database connection failed: {e}")
            return None
    return db_connection


def close_db():
    """Function to close the central database connection if it exists"""
    global db_connection
    if db_connection is not None:
        db_connection.close()
        db_connection = None
        logging.info("The database connection is now closed.")
        
        
#The tables for the database will be created
#Called in initialize_db
def create_tables(cur, db):
    """Function to create all necessary tables in the database"""
    try:
        #Create User Data Table
        cur.execute("""CREATE TABLE IF NOT EXISTS user (
                        user_id TEXT PRIMARY KEY,
                        user_name TEXT NOT NULL,
                        user_pwd TEXT NOT NULL)
                    """)

        #Create Habits Table
        cur.execute("""CREATE TABLE IF NOT EXISTS habits (
                        user_id TEXT,
                        habit_name TEXT NOT NULL,
                        habit_def TEXT,
                        habit_type TEXT,
                        habit_date TEXT,
                        habit_interval TEXT,
                        is_custom BOOLEAN DEFAULT 1,
                        PRIMARY KEY (user_id, habit_name),
                        FOREIGN KEY (user_id) REFERENCES user (user_id))
                    """)

        #Create Counter Table
        cur.execute("""CREATE TABLE IF NOT EXISTS counter (
                        user_id TEXT,
                        habit_name TEXT,
                        check_date TEXT,
                        check_time, TEXT,
                        habit_rep INTEGER DEFAULT 0,
                        habit_streak INTEGER DEFAULT 0,
                        PRIMARY KEY (user_id, habit_name, check_date),
                        FOREIGN KEY (user_id) REFERENCES user (user_id),
                        FOREIGN KEY (habit_name) REFERENCES habits (habit_name))
                    """)

        db.commit()
        logging.info("The tables were successfully created.")
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"An error occurred while creating tables: {e}")


# Predefined data will be added to the database for maintainance and test purposes
#Called in initialize_db
def insert_predef_user_data(db):
    """Function that inserts predefined user data into the database"""
    cur = db.cursor()
    try:
        cur.execute("""INSERT OR IGNORE INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)""",
                    ('test0101', 'testuser', 'pwd123!'))
        db.commit()
        logging.info("Predefined data inserted successfully")
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Failed to insert predefined data: {e}")        
        

#Function to initialize the database by calling create_tables() and insert_predef_user_data()
def initialize_db(cur, db):
    """
        Function that initializes the database by creating tables and 
        inserting predefined data using an existing connection (from main.py)
    """
    try:      
        #Create tables
        create_tables(cur, db)

        #Insert predefined user data
        insert_predef_user_data(cur, db)

        #Insert predefined habits
        from habit_manager import create_predef_habits
        create_predef_habits(cur, db)

        db.commit()
        logging.info("Database has been successfully created and initialized.")
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Failed to initialize the database: {e}")     
        
        
#Function to increment the counter data, used in counter_manager.py
def add_counter(db, user_id, habit_name, check_date, check_time, habit_rep, habit_streak):
    """
    Function to to add or update a counter record for a specific habit
    
    :param cur: Cursor for database operations
    :param db: Database connection object
    :param user_id: ID of the user
    :param habit_name: Name of the habit
    :param check_date: Date of the check (format: YYYY-MM-DD)
    :param check_time: Time of the check (format: HH:MM:SS)
    :param habit_rep: Number of repetitions
    :param habit_streak: Current streak value
    """
    try:
        cur = db.cursor()
        
        #Check if a record for the current date already exists
        cur.execute("""SELECT 1 FROM counter WHERE user_id = ? AND habit_name = ? AND check_date = ?""",
                    (user_id, habit_name, check_date))
        if cur.fetchone():
            logging.warning("There exists already an entry for this habit and date.")
            return
        
        #Insert new data
        cur.execute("""
            INSERT INTO counter (user_id, habit_name, check_date, check_time, habit_rep, habit_streak) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, habit_name, check_date, check_time, habit_rep, habit_streak))
        db.commit()
        logging.info("Counter data was successfully inserted.")
    
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"An error occurred while inserting counter data: {e}")