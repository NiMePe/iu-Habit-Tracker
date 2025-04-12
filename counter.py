"""
    This file contains the counter class.
    It contains methods for the user to mark a habit as checked,
    to increment the repetion and the streak counter, and to manually reset a streak in case of streak break.
    All methods call functions from 'counter_manager.py'
"""

import sqlite3
from counter_manager import increment_streak, increment_counter, check_habit, reset_streak

class Counter:
    def __init__(self, db_connection, user_id):
    
    """
    A class that represents a counter for habits to be tracked and checked.
    
    :param db_connection: sqlite3.connection 
        The database connection object that is used to interact with the database.
    :param user_id: str
        A unique identification of the user; used to associate habits with their account.
    """
    
        self.user_id = user_id
        #Database connection
        self.db = db_connection
        self.cur = self.db.cursor()
        
        
    def increment_streak(self, habit_name):
        """Method to increment the streak counter by 1"""
        increment_streak(self.cur, self.db, habit_name, self.user_id)
        
        
    def increment_counter(self, habit_name):
        """Method to increment the repetition counter by 1"""
        increment_counter(self.cur, self.db, habit_name, self.us
        
                          
    def check_habit(self):
        """Method to mark a habit as completed"""
        check_habit(self.cur, self.db, self.user_id)

                          
    def reset_streak(self):
        """Method to manually reset a streak"""
        reset_streak(self.cur, self.db, None, self.user_id)
                          
#This is for later tests
counter = Counter("test name", "test description")
counter.increment_streak()
print(counter)