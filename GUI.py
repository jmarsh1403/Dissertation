import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk

# Function to retrieve and display call log information
def fetch_call_log_info():
    # Get input values
    case_folder_directory = folder_directory_var.get()

    # Validate directory
    if not os.path.isdir(case_folder_directory):
        messagebox.showerror("Error", "Invalid directory path!")
        return

    # Construct database paths
    autopsy_db_path = os.path.join(case_folder_directory, "autopsy.db")
    creator_db_path = r"C:\Users\Jack\OneDrive - University of Gloucestershire\Diss\Diss Assignment\Dissertation\Creator.db"

    # Check if autopsy.db exists
    if not os.path.isfile(autopsy_db_path):
        messagebox.showerror("Error", f"Could not find the 'autopsy.db' database file at: {autopsy_db_path}")
        return

    # Clear previous results
    result_text.delete(1.0, tk.END)

    # Try to fetch call log data from the databases
    try:
        # Connect to the Autopsy database
        conn_autopsy = sqlite3.connect(autopsy_db_path)
        cursor_autopsy = conn_autopsy.cursor()

        # Query to retrieve phone numbers from the 'accounts' table
        query = """
        SELECT 
            a.account_unique_identifier AS phone_number
        FROM 
            accounts a
        WHERE 
            a.account_type_id = 3;
        """

        # Execute the query
        cursor_autopsy.execute(query)
        phone_numbers = cursor_autopsy.fetchall()

        # Extract the first three, two, and one digits from phone numbers
        first_three_digits = set()
        first_two_digits = set()
        first_digit = set()
        for phone_number in phone_numbers:
            if phone_number[0].startswith('+'):
                # Extract the first three digits after the '+'
                first_three_digits.add(phone_number[0][1:4])
                # Extract the first two digits after the '+'
                first_two_digits.add(phone_number[0][1:3])
                # Extract the first digit after the '+'
                first_digit.add(phone_number[0][1:2])

        # Close the Autopsy database connection
        conn_autopsy.close()

        # Connect to the Creator database
        conn_creator = sqlite3.connect(creator_db_path)
        cursor_creator = conn_creator.cursor()

        # Query to get all valid phone codes
        phone_code_query = "SELECT phonecode FROM Countries;"

        # Execute the query
        cursor_creator.execute(phone_code_query)
        valid_country_codes = {str(code[0]) for code in cursor_creator.fetchall()}

        # Close the Creator database connection
        conn_creator.close()

        # Compare and find valid country codes
        valid_autopsy_country_codes = first_three_digits.intersection(valid_country_codes)
        valid_autopsy_country_codes.update(first_two_digits.intersection(valid_country_codes))
        valid_autopsy_country_codes.update(first_digit.intersection(valid_country_codes))

        # Update the country code dropdown menu
        country_code_combobox['values'] = list(valid_autopsy_country_codes)

        # Display valid country codes in the GUI
        if valid_autopsy_country_codes:
            result_text.insert(tk.END, "Valid Country Codes:\n")
            result_text.insert(tk.END, "-" * 60 + "\n")
            for code in valid_autopsy_country_codes:
                result_text.insert(tk.END, f"{code}\n")
            result_text.insert(tk.END, "-" * 60 + "\n\n")
        else:
            result_text.insert(tk.END, "No valid country codes found.\n")
            return

        # Allow the user to select a country code
        selected_country_code = country_code_var.get()
        if not selected_country_code or selected_country_code not in valid_autopsy_country_codes:
            messagebox.showerror("Error", "Please select a valid country code!")
            return

        # Filter and display phone numbers based on the selected country code
        conn_autopsy = sqlite3.connect(autopsy_db_path)
        cursor_autopsy = conn_autopsy.cursor()

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

        cursor_autopsy.execute(query)
        results = cursor_autopsy.fetchall()

        if results:
            result_text.insert(tk.END, f"Filtered Call Log Information (Phone numbers starting with '+{selected_country_code}'):\n")
            result_text.insert(tk.END, "-" * 60 + "\n")
            for row in results:
                phone_number, file_name, file_path = row
                if str(phone_number).startswith(f'+{selected_country_code}'):
                    result_text.insert(tk.END, f"Phone Number: {phone_number}\n")
                    result_text.insert(tk.END, f"File Name: {file_name}\n")
                    result_text.insert(tk.END, f"File Path: {file_path}\n")
                    result_text.insert(tk.END, "-" * 60 + "\n")
        else:
            result_text.insert(tk.END, "No call log information found.\n")

        # Handle USA-specific area codes if the country code is 1
        if selected_country_code == '1':
            handle_usa_code()

        # Close the Autopsy database connection
        conn_autopsy.close()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"An error occurred while accessing the database: {e}")

# Function to handle USA-specific area codes
def handle_usa_code():
    # Path to the area_codes database
    area_codes_db_path = r"C:\Users\Jack\OneDrive - University of Gloucestershire\Diss\Diss Assignment\Dissertation\area_codes.db"

    # Verify the file path
    if not os.path.isfile(area_codes_db_path):
        messagebox.showerror("Error", "Database file does not exist at the specified path.")
        return

    try:
        # Connect to the area_codes database
        conn = sqlite3.connect(area_codes_db_path)
        cursor = conn.cursor()

        # Query to retrieve states and their area codes
        query = """
        SELECT 
            s.state_name, 
            a.area_code 
        FROM 
            States s
        JOIN 
            AreaCodes a ON s.id = a.state_id;
        """

        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        # Group area codes by state
        state_area_codes = {}
        for state_name, area_code in results:
            if state_name not in state_area_codes:
                state_area_codes[state_name] = []
            state_area_codes[state_name].append(area_code)

        # Display the states and their area codes
        if state_area_codes:
            result_text.insert(tk.END, "\nStates and their Area Codes:\n")
            result_text.insert(tk.END, "-" * 60 + "\n")
            for state_name, area_codes in state_area_codes.items():
                area_codes_str = ", ".join(area_codes)
                result_text.insert(tk.END, f"State: {state_name}, Area Codes: {area_codes_str}\n")
            result_text.insert(tk.END, "-" * 60 + "\n")
        else:
            result_text.insert(tk.END, "\nNo states or area codes found in the database.\n")

        # Close the area_codes database connection
        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"An error occurred while accessing the area_codes database: {e}")

# Function to browse and select the Autopsy case folder
def browse_folder():
    folder_path = filedialog.askdirectory(title="Select Autopsy Case Folder")
    if folder_path:
        folder_directory_var.set(folder_path)
        fetch_call_log_info()  # Automatically fetch call log info and update country codes

# Set up the Tkinter GUI window
root = tk.Tk()
root.title("Call Log Learner")
root.geometry("800x700")

# Create and organize frames
input_frame = ttk.Frame(root, padding="10")
input_frame.pack(fill=tk.X)

result_frame = ttk.Frame(root, padding="10")
result_frame.pack(fill=tk.BOTH, expand=True)

# Create labels, inputs, and buttons in the input frame
ttk.Label(input_frame, text="Select your Autopsy Case Folder:").grid(row=0, column=0, sticky=tk.W)

folder_directory_var = tk.StringVar()
folder_entry = ttk.Entry(input_frame, textvariable=folder_directory_var, width=50)
folder_entry.grid(row=0, column=1, padx=5, sticky=tk.W)

browse_button = ttk.Button(input_frame, text="Browse", command=browse_folder)
browse_button.grid(row=0, column=2, padx=5)

ttk.Label(input_frame, text="Select a Country Code:").grid(row=1, column=0, sticky=tk.W, pady=5)

country_code_var = tk.StringVar()
country_code_combobox = ttk.Combobox(input_frame, textvariable=country_code_var, width=10)
country_code_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)

fetch_button = ttk.Button(input_frame, text="Fetch Call Log Info", command=fetch_call_log_info)
fetch_button.grid(row=2, column=0, columnspan=3, pady=10)

# Scrolled text widget to display the results
result_text = scrolledtext.ScrolledText(result_frame, width=70, height=15)
result_text.pack(fill=tk.BOTH, expand=True)

# Start the Tkinter main loop
root.mainloop()