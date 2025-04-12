"""
    This file contains helper functions for the user class to create, change and authenticate a user profile.
    Functions are called in the user class.
"""

from getpass import getpass
import sqlite3

#Function to create the user name
def create_name(cur, db):
    """Function to create a user name"""
    while True:
        try:
            print("\nLet's create a user name: ")
            user_name = input("Please enter a user name you can easily memorize: ")
            cur.execute("SELECT user_id FROM user WHERE user_name = ?", (user_name,))
            if cur.fetchone():
                print("This user name is already taken. Please choose a different one.")
                continue

            name_correct = input(f"Is '{user_name}' correct? Type 'Y' for yes and 'N' for no: ").lower()
            if name_correct == "n":
                print("Let's try entering the name again.")
                continue
            elif name_correct != "y":
                print("Invalid input. Please type 'Y' for yes or 'N' for no.")
                continue

            return user_name
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred while creating user name: {e}")

            
#Function to create the user ID
def create_id(cur, db):
    """Function to create a user ID"""
    while True:
        try:
            print("\nNow let's create your unique user ID: ")
            id_part1 = input("Please type the first two letters of your first name: ")[:2]
            id_part2 = input("Please type the first two letters of your last name: ")[:2]
            id_part3 = input("Please type the month of your birth as number (eg. August = 08)").zfill(2)
            id_part4 = input("Please type the date of your birth (eg. August, 24th = 24)").zfill(2)
            user_id = f"{id_part1}{id_part2}{id_part3}{id_part4}"

            id_correct = input(f"Is this your ID: '{user_id}'? Type 'Y' for yes and 'N' for no: ").lower()
            if id_correct == "n":
                print("Let's try entering the ID again.")
                continue
            elif id_correct != "y":
                print("Invalid input. Please type 'Y' for yes or 'N' for no.")
                continue

            return user_id
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred while creating user ID: {e}")

            
#Function to create the user password
def create_pwd(cur, db):
    """Function to create a user password"""
    while True:
        try:
            print("\nLet's set up your user password.")
            user_pwd = getpass("\nPlease enter a secure password with at least 6 characters using numbers,"
                               "letters, and special characters: ")
            if len(user_pwd) < 6:
                print("Your password is too short. Please try again.")
                continue
            confirm_pwd = getpass("Please confirm your password: ")
            if confirm_pwd == user_pwd:
                return user_pwd
            else:
                print("Passwords do not match. Try again.")
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred while creating user password: {e}")

            
#Function to create a complete user profile
def create_profile(cur, db):
    """Function to create a new user with name, ID, and password"""
    try:
        user_name = create_name(cur, db)
        user_id = create_id(cur, db)
        user_pwd = create_pwd(cur, db)

        cur.execute("INSERT INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
                    (user_id, user_name, user_pwd))
        db.commit()
        print("User created successfully!")
        return user_id, user_name, user_pwd
    except sqlite3.Error as e:
        db.rollback()
        print(f"Error creating user: {e}")

        
#Function to change the profile
def change_profile(cur, db, user):
    """Function to allow a registered user to change their profile"""
    while True:
        try:
            print("\nWhat do you want to change?")
            print("1 = User Name")
            print("2 = Password")
            print("3 = User ID")
            print("4 = Delete Account")
            print("5 = Close Menu")

            #Prompt valid user input
            user_input = input("\nPlease enter a number (1, 2, 3, 4, or 5): ").strip()

            if user_input == 1:
                new_user_name = create_name(cur, db)
                cur.execute("UPDATE user SET user_name = ? WHERE user_id = ?", (new_user_name, user.user_id))
                db.commit()
                print(f"User name changed to '{new_user_name}'.")
            
            elif user_input == 2:
                new_user_pwd = create_pwd(cur, db)
                cur.execute("UPDATE user SET user_pwd = ? WHERE user_id = ?", (new_user_pwd, user.user_id))
                db.commit()
                print("Password changed successfully.")
            
            elif user_input == 3:
                new_user_id = create_id(cur, db)
                cur.execute("UPDATE user SET user_id = ? WHERE user_id = ?", (new_user_id, user.user_id))
                db.commit()
                print(f"User ID changed to '{new_user_id}'.")
            
            elif user_input == 4:
                print("\nDo you want to delete your user account?")
                confirm_delete = input("Please enter 'Y' for yes and 'N' for no: ").lower()
                if confirm_delete == "y":
                    confirm_input1 = getpass("Please enter your password: ")
                    confirm_input2 = input("To confirm deletion, enter your user ID: ")
                    if confirm_input1 == user.user_pwd and confirm_input2 == user.user_id:
                        cur.execute("DELETE FROM user WHERE user_id = ?", (user.user_id,))
                        db.commit()
                        print("YOur User account was successfully deleted.")
                        break
                    else:
                        print("Password or user ID were incorrect. Account deletion was canceled.")
                else:
                    print("Account deletion was canceled.")
            
            elif user_input == 5:
                print("Exiting profile management.")
                break
            
            else:
                print("Invalid input. Please enter a number between 1 and 5.")

        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred when changing profile: {e}")

            
            
#Function for authentication before login
def user_auth(cur, db):
    """Authenticate a user by verifying their username or user ID and password"""
    while True:
        try:
            print("\nUser Authentication")
            identifier = input("Please enter your username or user ID: ").strip()
            cur.execute(
                "SELECT user_pwd FROM user WHERE user_name = ? OR user_id = ?", 
                (identifier, identifier)
            )
            result = cur.fetchone()
            
            if result:
                stored_pwd = result[0]
                input_pwd = getpass("Please enter your password: ")
                if input_pwd == stored_pwd:
                    print("Authentication successful!")
                    return identifier
                else:
                    print("Incorrect password. Please try again.")
            else:
                print("No user found with the provided username or user ID.")
                print("Do you want to create a new profile?")
                create_choice = input("Please enter 'Y' for yes and 'N' for no: ").strip().lower()
                if create_choice == "y":
                    create_profile(cur, db)
                    print("A new profile was created successfully! Please log in again.")
                elif create_choice == "n":
                    print("Exiting program. Thanks and good bye!")
                    exit()
                else:
                    print("Invalid input. Please enter 'Y' or 'N'.")
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred during authentication: {e}")
