import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Function to retrieve and display call log information
def fetch_call_log_info():
    # Get input values
    case_created = case_created_var.get()
    case_folder_directory = folder_directory_var.get()

    # Validate directory
    if not os.path.isdir(case_folder_directory):
        messagebox.showerror("Error", "Invalid directory path!")
        return

    # Construct database path
    database_path = os.path.join(case_folder_directory, "autopsy.db")
    if not os.path.isfile(database_path):
        messagebox.showerror("Error", f"Could not find the 'autopsy.db' database file at: {database_path}")
        return

    # Clear previous results
    result_text.delete(1.0, tk.END)

    # Try to fetch call log data from the database
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query to retrieve phone numbers and associated file details
        query = """
        SELECT 
            a.account_unique_identifier AS phone_number,
            f.name AS file_name,
            f.parent_path AS file_path
        FROM 
            accounts a
        JOIN 
            tsk_files f ON a.account_id = f.obj_id
        WHERE 
            a.account_type_id = 3;
        """
        
        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        # Display results in the text box
        if results:
            for row in results:
                phone_number, file_name, file_path = row
                if str(phone_number).startswith('+'):  # Only display if phone number starts with '+'
                    result_text.insert(tk.END, f"Phone Number: {phone_number}\n")
                    result_text.insert(tk.END, f"File Name: {file_name}\n")
                    result_text.insert(tk.END, f"File Path: {file_path}\n")
                    result_text.insert(tk.END, "-" * 60 + "\n")
        else:
            result_text.insert(tk.END, "No call log information found.\n")

        # Close the database connection
        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"An error occurred while accessing the database: {e}")

# Set up the Tkinter GUI window
root = tk.Tk()
root.title("Call Log Learner")
root.geometry("800x700")

# Create labels, inputs, and buttons
tk.Label(root, text="Have you created an Autopsy case? (yes/no):").pack(pady=5)
case_created_var = tk.StringVar(value="yes")
tk.Entry(root, textvariable=case_created_var).pack(pady=5)

tk.Label(root, text="Enter your Autopsy Case Folder Directory:").pack(pady=5)
folder_directory_var = tk.StringVar()
tk.Entry(root, textvariable=folder_directory_var).pack(pady=5)

# Button to fetch the call log information
fetch_button = tk.Button(root, text="Fetch Call Log Info", command=fetch_call_log_info)
fetch_button.pack(pady=10)

# Scrolled text widget to display the results
result_text = scrolledtext.ScrolledText(root, width=70, height=15)
result_text.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()