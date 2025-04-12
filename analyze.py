"""
    This file contains functions for the logged-in user to analyze their data.
    The user will be able to view all, all custom, and all predefined habits.
    They can filter for daily and for weekly habits.
    The user can also view their streaks.
    The analysis file makes use of the pandas and sqlite libraries.
"""

import sqlite3
import pandas as pd

####Functions to show habits according to creator and periodicity

#Functions to display habits depending on their creator (predefined vs. custom vs. all)
def show_predef_habits(cur):
    """Function to display all predefined habits"""
    try:
        #Fetch predefined habits
        cur.execute("SELECT habit_name, habit_def, habit_type, habit_interval FROM habits WHERE is_custom = 0")
        habits = cur.fetchall()

        if not habits:
            print("\nThere are currently no predefined habits.")
            return

        #Create a table 
        habits_df = pd.DataFrame(habits, columns=["Name", "Description", "Type", "Interval"])
        print("\nHere you can see all predefined habits:")
        print(habits_df.to_string(index=False))
    except sqlite3.Error as e:
        print(f"An error occurred while displaying predefined habits: {e}")
        
        
def show_custom_habits(cur, user_id):
    """Function to display all custom habits for a specific user"""
    try:
        #Fetch custom habits from the user
        cur.execute(
            "SELECT habit_name, habit_def, habit_type, habit_interval FROM habits WHERE user_id = ? AND is_custom = 1",
            (user_id,)
        )
        habits = cur.fetchall()

        if not habits:
            print("\nThere are currently no custom habits.")
            return

        #Create a table 
        habits_df = pd.DataFrame(habits, columns=["Name", "Description", "Type", "Interval"])
        print("\nHere you can see your custom habits:")
        print(habits_df.to_string(index=False))
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving your habits: {e}")
       
    
def show_all_habits(cur, user_id):
    """Function to display all habits (custom and predefined)"""
    try:
        custom_habits = show_custom_habits(cur, user_id)
        predef_habits = show_predef_habits(cur)
        if custom_habits.empty and predef_habits.empty: #.empty checks for empty cells
            print("\nNo habits found.")
            return pd.DataFrame(columns=["Name", "Description", "Type", "Interval", "Custom"])
        
        #Add a "Custom" column for the user to distinct between own and predefined habits
        custom_habits["Custom"] = True
        predef_habits["Custom"] = False
        
        #Combine both tables (of predefined and custom habits)
        all_habits = pd.concat([custom_habits, predef_habits], ignore_index=True)
        return all_habits
    except sqlite.Error as e:
        print(f"An error occurred while joining custom with predefined habits: {e}")
        return pd.DataFrame()

    
#Functions to display habits depending on their interval (daily vs. weekly)
def show_daily_habits(cur, user_id):
    """Function to return all daily habits (custom and predefined)"""
    try:
        cur.execute(
            """SELECT habit_name, habit_def, habit_type, habit_interval, is_custom FROM habits WHERE 
            (user_id = ? OR is_custom = 0) AND habit_interval = 'Daily'""",
            (user_id,)
        )
        habits = cur.fetchall()
        if not habits:
            print("\nNo daily habits found.")
            return pd.DataFrame(columns=["Name", "Description", "Type", "Interval", "Custom"])
        return pd.DataFrame(habits, columns=["Name", "Description", "Type", "Interval", "Custom"])
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving daily habits: {e}")
        return pd.DataFrame()


def show_weekly_habits(cur, user_id):
    """Function to return all weekly habits"""
    try:
        cur.execute(
            """SELECT habit_name, habit_def, habit_type, habit_interval, is_custom FROM habits WHERE 
            (user_id = ? OR is_custom = 0) AND habit_interval = 'Weekly'""",
            (user_id,)
        )
        habits = cur.fetchall()
        if not habits:
            print("\nNo weekly habits found.")
            return pd.DataFrame(columns=["Name", "Description", "Type", "Interval", "Custom"])
        return pd.DataFrame(habits, columns=["Name", "Description", "Type", "Interval", "Custom"])
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving weekly habits: {e}")
        return pd.DataFrame()



####Functions to analyze counter data

def show_longest_streak(cur):
    """Function to display the streaks of all habits in descending order"""
    try:
        cur.execute("SELECT habit_name, habit_streak FROM counter ORDER BY habit_streak DESC")
        streaks = cur.fetchall()
        if not streaks:
            print("\nNo streak data available.")
            return pd.DataFrame(columns=["Habit", "Streak"])
        return pd.DataFrame(streaks, columns=["Habit", "Streak"])
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving longest streaks: {e}")
        return pd.DataFrame()

    
def show_streak_break(cur):
    """Function to display all habits where the streak is currently broken"""
    try:
        cur.execute("SELECT habit_name, habit_streak FROM counter WHERE habit_streak = 0")
        streaks = cur.fetchall()
        if not streaks:
            print("\nNo broken streaks found.")
            return pd.DataFrame(columns=["Habit", "Streak"])
        return pd.DataFrame(streaks, columns=["Habit", "Streak"])
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving streak breaks: {e}")
        return pd.DataFrame()

    
def show_streak_for_specific_habit(cur, user_id):
    """Function to display streak data for a specific habit"""
    try:
        #Display all habits
        all_habits = show_all_habits(cur, user_id)
        if all_habits.empty:
            print("\nNo habits were found.")
            return

        print("\nHere are all your habits:")
        print(all_habits.to_string(index=False))

        #User selects a specific habit
        habit_name = input("\nEnter the exact name of a habit to get its streak: ").strip()
        cur.execute(
            "SELECT habit_streak FROM counter WHERE habit_name = ? AND user_id = ?", 
            (habit_name, user_id)
        )
        streak = cur.fetchone()
        if streak:
            print(f"\nThe current streak for '{habit_name}' is: {streak[0]}.")
        else:
            print(f"\nNo streak data was found for '{habit_name}'.")
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving the streak for '{habit_name}': {e}")


def show_rep_number(cur, user_id):
    """Function to calculate and display the total number of repetitions of a given habit"""
    try:
        #Display all habits
        all_habits = show_all_habits(cur, user_id)
        if all_habits.empty:
            print("\nNo habits were found to calculate counters.")
            return

        print("\nHere are all your habits:")
        print(all_habits.to_string(index=False))

        #User selects a specific habit
        habit_name = input("\nEnter the name of the habit to calculate its counter: ").strip()
        if habit_name not in all_habits["Name"].values:
            print("Invalid habit name. Please try again.")
            return

        #Calculate the total counter
        cur.execute(
            "SELECT SUM(habit_rep) FROM counter WHERE habit_name = ? AND user_id = ?", 
            (habit_name, user_id)
        )
        total_count = cur.fetchone()[0]

        if total_count:
            print(f"\nThe total count for '{habit_name}' is {total_count}.")
        else:
            print(f"\nNo counter data was found for '{habit_name}'.")

    except sqlite3.Error as e:
        print(f"An error occurred while calculating the counter for '{habit_name}': {e}")
