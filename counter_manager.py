"""
    File that contains helping functions to manage the database connection and
    user interaction with the counter of the habit tracker.
    Functions will be called in the counter class.
"""

import sqlite3
from datetime import datetime, timedelta
from analyze import show_all_habits
from db import add_counter

#Functions defining the update of the repetition and the streak counters
#Called in check_habit()
def increment_streak(cur, db, habit_name, user_id):
    """Function that increments the streak of a habit"""
    try:
        now = datetime.now()
        check_date = now.strftime('%Y-%m-%d')  #Current date
        check_time = now.strftime('%H:%M:%S')  #Current time
        
        #Check the last streak value
        cur.execute(
            "SELECT habit_streak FROM counter WHERE habit_name = ? AND user_id = ? ORDER BY check_date DESC LIMIT 1",
            (habit_name, user_id)
        )
        last_record = cur.fetchone()

        if last_record:
            last_streak, last_date = last_record
            last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
        else:
            last_streak, last_date = 0, None
        
        #Find out the habit's interval
        cur.execute("SELECT habit_interval FROM habits WHERE habit_name = ? AND user_id = ?", (habit_name, user_id))
        interval = cur.fetchone()
        
        #Update streak counter according to the habit's interval
        if interval and interval[0] == "Weekly" and last_date and last_date >= now.date() - timedelta(days=7):
            new_streak = last_streak + 1
        elif interval and interval[0] == "Daily" and last_date == now.date():
            new_streak = last_streak + 1
        else:
            new_streak = 1

        #Call add_counter function from db.py to update streak counter
        add_counter(cur, db, user_id, habit_name, check_date, check_time, 0, new_streak)
        print(f"The streak for '{habit_name}' has been incremented to {new_streak}.")
    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while incrementing streak for '{habit_name}': {e}")


def increment_counter(cur, db, habit_name, user_id):
    """
        Function that increments the number of repetions of a given habit 
        and that automatically increments the streak counter
    """
    try:
        now = datetime.now()
        check_date = now.strftime('%Y-%m-%d')  #Current date
        check_time = now.strftime('%H:%M:%S')  #Current time
        
        #Validate if the habit exists
        cur.execute("SELECT 1 FROM counter WHERE habit_name = ? AND user_id = ?", (habit_name, user_id))
        if not cur.fetchone():
            print(f"The habit '{habit_name}' does not exist.")
            return  
                
        #Check the last repetition value
        cur.execute(
            "SELECT habit_rep FROM counter WHERE habit_name = ? AND user_id = ? ORDER BY check_date DESC LIMIT 1",
            (habit_name, user_id)
        )
        last_rep = cur.fetchone()
        
        if last_rep and last_rep[1] == check_date:
            new_rep = last_rep[0] + 1
        else:
            new_rep = 1

        #Call add_counter function from db.py to update repetition counter
        add_counter(cur, db, user_id, habit_name, check_date, check_time, new_rep, 0)
        print(f"The number of repetitions of '{habit_name}' has been incremented to {new_rep}.")
        
        #Automatically increment streak
        increment_streak(cur, db, habit_name, user_id)              
    
    except sqlite3.Error as e:
        db.rollback()
        print(f"Error while incrementing counter for '{habit_name}': {e}")


#Function to mark a habit as checked + update counters
def check_habit(cur, db, user_id):
    """
        Function that lets the user check a given habit and that
        automatically increments the repetition counter
    """
    try:
        #Display all habits using imported "show_all_habits" function
        all_habits = show_all_habits(cur, user_id)
        if all_habits.empty:
            print("\nNo habits found to check.")
            return

        print("\nHere you can see all habits: ")
        print(all_habits.to_string(index=False))

        #User input 1: Enter correct habit name
        while True:
            habit_name = input("\nEnter the name of the habit you want to check: ").strip()
            if habit_name in all_habits["Name"].values:
                selected_habit = all_habits[all_habits["Name"] == habit_name].iloc[0]
                break
            print("Invalid habit name. Please enter a valid habit name from the list.")

        habit_interval = selected_habit["Interval"]

        #User input 2: Check the habit according to its interval
        now = datetime.now()
        check_date = now.strftime('%Y-%m-%d')  #Current date
        check_time = now.strftime('%H:%M:%S')  #Current time
        
        if habit_interval == "Daily":
            print(f"Did you practice '{habit_name}' today ({check_date})?") 
            check_input = input("Please type 'Y' for yes and 'N' for no: ").lower()
        elif habit_interval == "Weekly":
            print(f"Did you practice '{habit_name}' in the past week or today ({check_date})?")
            check_input = input("Please type 'Y' for yes and 'N' for no: ").lower()
        else:
            raise ValueError("Invalid periodicity. Neither 'Daily' nor 'Weekly'.")

        if check_input == "y": 
            #Call add_counter function from db.py to mark habit as checked
            add_counter(cur, db, user_id, habit_name, check_date, check_time, 1,1)
            print(f"The habit '{habit_name}' was marked as checked.")
            
             #Automatically increment the repetition counter (and indirectly the streak)
            increment_counter(cur, db, habit_name, user_id)
        else:
            print(f"The habit '{habit_name}' wasn't marked as checked.")

    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while checking a habit: {e}")


#Function to manually reset the streak of a given habit
def reset_streak(cur, db, habit_name, user_id):
    """Function to allow manual reset of the streak of a given habit by the user"""
    try:
        #Display all habits using imported "show_all_habits" function
        print("\nHere you can see all habits:")
        all_habits = show_all_habits(cur, user_id)
        if all_habits.empty: #Check for empty cells in pandas dataframe
            print("\nNo habits available to reset streaks.")
            return
        print(all_habits.to_string(index=False))

        #Ask user if they want to reset streak manually
        while True:
            print("Would you like to manually reset a streak?") 
            manual_reset = input("Please type 'Y' for yes and 'N' for no: ").strip().lower()
            if manual_reset == 'y':
                habit_name = input("\nPlease enter the name of the habit you want to reset the streak for: ").strip()
                if habit_name in all_habits["Name"].values:
                    cur.execute(
                        "UPDATE counter SET habit_streak = 0 WHERE habit_name = ? AND user_id = ?",
                        (habit_name, user_id)
                    )
                    db.commit()
                    print(f"The streak for '{habit_name}' has been manually reset.")
                    return
                else:
                    print("Invalid habit name. Please choose a habit from the list.")
            elif manual_reset == 'n':
                print("No streaks were reset.")
                return
            else:
                print("Please enter 'Y' or 'N'.")

    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while resetting streak for '{habit_name}': {e}")
        
        
