"""
This file contains the main programm to guide a user through
the habit tracker backend program. It makes use of all class
files such as the habit class, the user class, the counter 
class, the database file, and the analyse file.
"""

import counter
import analyze
from db import get_db, close_db, initialize_db
from habits import Habit
from user import user_auth, create_profile

                

####Functions for main menu
#Step 1: Create Welcome Screen
def welcome_menu():
    """Function to display welcome screen"""
    print("""
    **************************************
     WELCOME TO THE HABIT TRACKER PROGRAM
    **************************************
    """)
    
    print("""
    A habit tracker is a tool to help a person achieving a personal 
    goal by monitoring the implementation of a (new) habit.

    This habit tracker is a backend program with no graphical user interface.
    You will therefore be guided by questions with multiple choice options.

    This habit tracker will provide predefined habits from the field of 
    stress reduction that you could use for tracking. You will also be 
    able to define own custom habits for tracking purpose.

    Furthermore, the habit tracker will store your data within a database file
    that you save locally on your own computer. The data will then be used to
    provide you the opportunity to analyse your own tracking data.
    """)


#Step 2: Check if database exists or if new one is needed
def database_needed():
    """
    Function to check if a database exists and initialize it if needed.
    Provides the user with the option to create a new database or exit the program.
    """
    print("To be able to use the program, a local database file must be created.")
    print("The program will now check whether a database exists.")
   
    db = get_db() #Connecting to central database in db.py
        
    if not db: #If connection to database not possible: create or exit?
        print("No database connection could be established.")
        while True:    
            print("What would you like to do?")
            print("1 = Create a new database")
            print("2 = Exit program")
            db_input = input("Please enter your choice (1 or 2): ").strip()

            if db_input == "1":
                print("Attempting to create a new database...")
                try:
                    db = get_db()
                    if not db:
                        raise sqlite3.Error("Database creation failed.")
                        cur= db.cursor()
                        #Use of function from the db.py file to initialize database
                        initialize_db(cur, db)
                        print("Database has been successfully created and initialized.")
                        break
                except sqlite3.Error as e: #Error message in case connection is still not possible   
                    print(f"An error occurred while creating a new database. Error: {e}")
                    print("Please check if you have write permissions in the directory or if the database name is valid.")
                    continue
               
            elif db_input == "2":
                print("Thanks for participating.\nYou will now exit the program.")
                return None, None 

            else:
                print("Invalid input. Please enter '1' or '2'.") 

    cur = db.cursor()
    try:
        #Check whether the tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        if not tables:  #In case tables do not exist
            print("No tables were found. Initializing database...")
            initialize_db(cur, db)
            print("Database has been successfully created and initialized.")
    except sqlite3.Error as e:
        print(f"An error occurred while checking the database: {e}. Exiting program.")
        return None, None
    
    return db, cur


#Step 3: Login Menu
def login_user_menu():
    """Function that represents a login menu"""
    print("Do you aready have created a user profile?")
    log_input = input("Yes = 1, No = 2, Exit = 3")
    if log_input == "1":
        print("""
        **************************************
              LOGIN TO YOUR USER PROFILE
        **************************************
        """)
        user_auth()
    elif log_input == "2":
        print("""
        **************************************
                CREATE A USER PROFILE
        **************************************
        """)
        create_profile()
    elif log_input == "3":
        return ("Thanks for participating.\nYou will now exit the program.")



#Step 4: Main User Menu after successful login
def main_user_menu():
    """Function that represents the main menu with 5 options"""
    print("""
    *****************************************
            WELCOME TO THE MAIN MENU
    *****************************************
    """)
    print("""
    Within this menu, you can either view, change, or update your habits.
    You can also edit your user profile or exit the program.
    """)
    print("What do you want to do?")
    print("""
    ****************************
      1 VIEW HABITS & STREAKS
    ****************************
    """)
    print("""
    ********************
      2 CHANGE HABITS
    ********************
    """)
    print("""
    ****************************
     3 UPDATE HABITS & STREAKS
    ****************************
    """)
    print("""
    ********************
      4 CHANGE PROFILE
    ********************
    """)
    print("""
    ********************
           5 EXIT
    ********************    
    """)

    
#Step 4.1: VIEW HABITS & STREAKS    
def view_habits(cur, user_id):
    """Function to represent a menu with options to display habits and streaks"""
    while True:
        print("""
        ******************************************
                  1 VIEW HABITS & STREAKS
        ******************************************
        1. Predefined Habits
        2. Custom Habits
        3. All Habits
        4. Current Daily Habits
        5. Current Weekly Habits
        6. Longest Streak
        7. Streak Breaks
        8. Streak for Specific Habit
        9. Total Repetitions for a Habit
        10. Return to Main Menu
        *****************************************
        """)
        choice = input("Please select an option (1-10): ").strip()
        
        if choice == "1":
            analyse.show_predef_habits(cur)
        elif choice == "2":
            analyse.show_custom_habits(cur, user_id)
        elif choice == "3":
            analyse.show_all_habits(cur, user_id)
        elif choice == "4":
            habits = analyse.show_daily_habits(cur, user_id)
        elif choice == "5":
            habits = analyse.show_weekly_habits(cur, user_id)
        elif choice == "6":
            streaks = analyse.show_longest_streak(cur)
        elif choice == "7":
            streaks = analyse.show_streak_break(cur)
        elif choice == "8":
            analyse.show_streak_for_specific_habit(cur, user_id)
        elif choice == "9":
            analyse.show_rep_number(cur, user_id)
        elif choice == "10":
            print("Returning to the main menu.")
            break
        else:
            print("Invalid input. Please select a number between 1 and 10.")


#Step 4.2: CHANGE HABITS
def change_habits(cur, db, user_id):
    """Function thats allows the user to create, delete, or edit habits"""
    while True:
        print("""
        *****************************************
                    2 CHANGE HABITS
        *****************************************
        1. Create Custom Habit
        2. Delete Habit
        3. Edit Habit
        4. Return to Main Menu
        *****************************************
        """)
        choice = input("Please select an option (1-4): ").strip()

        if choice == "1":
            print("\nCreating a new custom habit...")
            habit_instance = Habit(db, user_id, "", "", "", None, "")
            habit_instance.create_custom_habits()
            print("Custom habit was successfully created!")
        
        elif choice == "2":
            print("\nDeleting a habit...")
            habit_instance = Habit(db, user_id, "", "", "", None, "")
            habit_instance.delete_habit(habit_name)
        
        elif choice == "3":
            print("\nEditing a habit...")
            habit_instance = Habit(db, user_id, "", "", "", None, "")
            habit_instance.edit_habit(habit_name)
                    
        elif choice == "4":
            print("Returning to the main menu.")
            break
        
        else:
            print("Invalid input. Please select a number between 1 and 4.")


#Step 4.3: UPDATE HABITS & STREAKS
def update_habits(cur, db, user_id):
    """
        Funciton that allows the user to check a habit, to reset streaks, 
        or to manually update counters and streaks.
    """
    while True:
        print("""
        ******************************************
                 3 UPDATE HABITS & STREAKS
        ******************************************
        1. Check a Habit
        2. Reset a Streak
        3. Manually Increment Counter
        4. Manually Increment Streak
        5. Return to Main Menu
        *****************************************
        """)
        choice = input("Please select an option (1-5): ").strip()

        if choice == "1":
            print("\nMarking a habit as checked...")
            print("Note: The repetition counter and the streak will be updated automatically.")
            counter.check_habit(cur, db, user_id)
            print("Habit successfully checked, counter and streak successfully incremented!")
        
        elif choice == "2":
            print("\nResetting a streak...")
            counter.reset_streak(cur, db, user_id)
            print("Streak reset successfully!")
        
        elif choice == "3":
            print("\nManual Increment: Counter")
            print("Note: Use this option only if the habit check was forgotten.")
            habit_name = input("Please enter the name of the habit for which to increment the counter: ").strip()
            counter.increment_counter(cur, db, habit_name, user_id)
            print("Counter incremented successfully!")
        
        elif choice == "4":
            print("\nManual Increment: Streak")
            print("Note: Use this option only if the habit check was forgotten.")
            habit_name = input("Please enter the name of the habit for which to increment the streak: ").strip()
            counter.increment_streak(cur, db, habit_name, user_id)
            print("Streak incremented successfully!")
        
        elif choice == "5":
            print("Returning to the main menu.")
            break
        
        else:
            print("Invalid input. Please select a number between 1 and 5.")

            
#Step 4.4: CHANGE PROFILE
def change_profile(cur, db, user_id):
    """Function that allows the user to edit their profile data"""
    while True:
        print("""
        *****************************************
                    4 CHANGE PROFILE
        *****************************************
        1. Edit or Delete Profile Data
        2. Return to Main Menu
        *****************************************
        """)
        choice = input("Please select option 1 or 2: ").strip()

        if choice == "1":
            print("\nEditing profile information...")
            user_instance = user.User(db, user_id=user_id)
            user_instance.change_profile()
            print("Profile successfully updated!")
        elif choice == "2":
            print("Returning to the main menu.")
            break
        else:
            print("Invalid input. Please select a number between 1 and 5.")

            
def main():
    """Function to run the habit tracker program"""
    try:
        #Step 1: Welcome Screen
        welcome_menu()

        #Step 2: Database Setup
        db, cur = database_needed() #Connection and cursor from database_needed
        if not db or not cur:
            print("Failed to connect to the database. Exiting program.")
            return
        
        #Step 3: User Authentication
        user_id = login_user_menu()
        if not user_id:
            print("Exiting program. Thanks and goodbye!")
            return
                
        #Step 4: Main User Menu
        while True:
            main_user_menu()
            input_main_menu = input("Please choose option 1, 2, 3, 4, or 5: ").strip()

            #4.1 VIEW HABITS & STREAKS
            if input_main_menu == "1":
                view_habits(cur, user_id)

            #4.2 CHANGE HABITS
            elif input_main_menu == "2":    
                change_habits(cur, db, user_id)

            #4.3 UPDATE HABITS & STREAKS
            elif input_main_menu == "3":
                update_habits(cur, db, user_id)

            #4.4 CHANGE PROFILE
            elif input_main_menu == "4":
                change_profile(cur, db, user_id)

            #4.5 EXIT
            elif input_main_menu == "5":
                print("Thanks for participating.\nYou will now be logged out.")
                break
            
            else:
                print("Invalid input. Please choose a valid option.")
    except sqlite3.Error as e:
        print(f"An unexpected database error occurred: {e}")
    finally:
        if cur:
            cur.close()
        close_db()
    
main()
                   
                      
                          
        