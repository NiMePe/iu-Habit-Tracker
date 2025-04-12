"""
    This file contains the user class.
    It allows a given user to create and edit their profile.
    It also contains a method to authenticate a user instance before viewing or manipulating their data.
    For this purpose, the class's methods call the respective functions from 'user_manager.py'
"""

from user_manager import create_name, create_id, create_pwd, change_profile, user_auth

class User:
    def __init__(self, db_connection, user_name: str = None, user_id: str = None, user_pwd: str = None):
    
    """ 
    A class that represents a user of the habit tracker. 
    
    :param db_connection: sqlite3.Connection 
        The database connection object used to interact with the database.
    :param user_name: str, optional
        The name chosen by the user.
    :param user_id: str, optional
        A unique identifier for the user to handle name duplications.
    :param user_pwd: str, optional
        The password chosen by the user for authentication.
    """ 
    
        self.user_name = user_name
        self.user_id = user_id
        self.user_pwd = user_pwd
        #Database connection
        self.db = db_connection
        self.cur = self.db.cursor()
        
        
    def create_name(self):
        """Method to create a unique user name"""
        self.user_name = create_name(self.cur, self.db)

        
    def create_id(self):
        """Method to create a unique user ID"""
        self.user_id = create_id(self.cur, self.db)

        
    def create_pwd(self):
        """Method to create the user password with 6 characters"""
        self.user_pwd = create_pwd(self.cur, self.db)
    
    
    def create_profile(self):
        """Method to create the entire user profile"""
        self.create_name()
        self.create_id()
        self.create_pwd()
           
            
    def change_profile(self):
        """Method to edit user name, password, user ID, or to delete entire account"""
        change_profile(self.cur, self.db, self, create_name, create_pwd, create_id)

                  
    def user_auth(self):
        """Method for authenticating a user profile before login"""
        user_auth(self.cur, self)

    
