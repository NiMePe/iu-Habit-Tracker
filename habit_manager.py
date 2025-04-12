"""
    File that contains helper functions for the habit class to
    -create custom and predefined habits
    -delete habits
    -edit habits
    Functions will be called in the habit class.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from analyze import show_custom_habits

#Functions to create habits
def create_predef_habits(cur, db):
    """Function to insert predefined habits into the database"""
    predef_habits = [
        ('Progressive Muscle Relaxation', 'It is a method to deeply relax the muscles by first tensing and relaxing each muscle group.', 'Relaxing', '2024-05-15', 'Daily', 0),
        ('Mindfulness Meditation', 'It is an approach to reduce stress by observing one\'s own body, thoughts, and feelings without judging them.', 'Relaxing', '2024-05-15', 'Weekly', 0),
        ('Journaling', 'It is a method to channel negative thoughts by positively reviewing the day.', 'Cognitive', '2024-05-15', 'Daily', 0),
        ('Week Planning', 'It is a method to reduce stress by carefully planning appointments for the next week.', 'Cognitive', '2024-05-15', 'Weekly', 0),
        ('Yoga', 'It is the act of combining special movements with mindfulness and breathing techniques.', 'Physical', '2024-05-15', 'Daily', 0),
        ('Jogging', 'It is the act of gentle running.', 'Physical', '2024-05-15', 'Weekly', 0)
    ]
    try:
        for habit in predef_habits:
            cur.execute(
                "INSERT INTO habits (habit_name, habit_def, habit_type, habit_date, habit_interval, is_custom) VALUES (?, ?, ?, ?, ?, ?)", habit
            )
        db.commit()
        print("Predefined habits have been successfully inserted.")
    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while inserting predefined habits: {e}")

    
def create_custom_habits(cur, db, user_id):
    """Function to allow a user to create custom habits"""
    print("In this menu, you can create your own custom habits.")
    print("Please answer the following questions:")

    try:
        habit_name = input("\nWhat is the name of the habit you want to create?\n")
        habit_def = input("\nPlease write a short definition of your habit.\n")
        habit_type = input("\nWhat could be the generic term of your habit (e.g., 'Relaxing', 'Cognitive', 'Physical', etc.)?\n")
        habit_date = datetime.now().strftime('%Y-%m-%d')

        while True:
            habit_interval = input("\nDo you want to practice your habit daily or weekly? (Type 'd' for daily and 'w' for weekly):\n").lower()
            if habit_interval == 'd':
                habit_interval = 'Daily'
                break
            elif habit_interval == 'w':
                habit_interval = 'Weekly'
                break
            else:
                print("Invalid input. Please type 'd' for daily or 'w' for weekly.")

        # Insert custom habit into the database
        cur.execute("INSERT INTO habits (user_id, habit_name, habit_def, habit_type, habit_date, habit_interval, is_custom) VALUES (?, ?, ?, ?, ?, ?, 1)",
                    (user_id, habit_name, habit_def, habit_type, habit_date, habit_interval))
        db.commit()
        print(f"The habit '{habit_name}' has been successfully saved.")
    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while creating your custom habit: {e}")

        
#Functions to change habits        
def delete_custom_habit(cur, db, user_id):
    """Function to delete a habit"""
    print("\nDo you want to delete one of your custom habits?")
    show_custom_habits(cur) #Shows existing habits
    custom_input = input("Type 'Y' for yes and 'N' for no: ").lower()

    if custom_input == "y":
        while True:
            try:
                del_name_input = input("\nPlease enter the name of the habit you want to delete: ")
                #Validation if the habit exists
                cur.execute("SELECT 1 FROM habits WHERE habit_name = ? AND user_id = ?", (del_name_input, user_id))
                if not cur.fetchone():
                    print(f"The habit '{del_name_input}' does not exist.")
                    return
                #Then delete
                cur.execute("DELETE FROM habits WHERE habit_name = ? AND user_id = ?", 
                            (del_name_input, user_id))
                db.commit()
                print(f"The habit '{del_name_input}' was successfully deleted.")
                break
            
            except sqlite3.Error as e:
                db.rollback()
                print(f"An error occurred while deleting your habit: {e}. Please try again.")
    else:
        print("No habits were deleted.")

        
def edit_custom_habit(cur, db, user_id):
    """Function to edit the periodicity of a habit"""
    print("\nDo you want to edit the periodicity of your custom habits?")
    show_custom_habits(cur) #Shows existing habits
    custom_input = input("Type 'Y' for yes and 'N' for no: ").lower()

    if custom_input == "y":
        while True:
            try:
                habit_name = input("\nPlease enter the name of the habit you want to edit: ")
                #Validation if the habit exists
                cur.execute("SELECT 1 FROM habits WHERE habit_name = ? AND user_id = ?", (habit_name, user_id))
                if not cur.fetchone():
                    print(f"The habit '{habit_name}' does not exist.")
                    return
                
                periodicity_input = input("\nDo you want to set the periodicity to 'Weekly' or 'Daily'? Please enter 'W' or 'D'): ").lower()
                
                if periodicity_input == "d":
                    new_interval = "Daily"
                    #Now edit
                    cur.execute("UPDATE habits SET habit_interval = ? WHERE habit_name = ? AND user_id = ?", 
                        (new_interval, habit_name, user_id))
                    db.commit()
                    print(f"The periodicity of habit '{habit_name}' has been successfully updated to '{new_interval}'.")
                    break
                elif periodicity_input == "w":
                    new_interval = "Weekly"
                    cur.execute("UPDATE habits SET habit_interval = ? WHERE habit_name = ? AND user_id = ?", 
                        (new_interval, habit_name, user_id))
                    db.commit()
                    print(f"The periodicity of habit '{habit_name}' has been successfully updated to '{new_interval}'.")
                    break
                else:
                    print("Invalid input. Please enter 'W' for Weekly or 'D' for Daily.")
            except sqlite3.Error as e:
                db.rollback()
                print(f"An error occurred while editing your habit: {e}. Please try again.")
    else:
        print("No habits were edited.")