import os
import sqlite3

def call_log_learner():
    print("Welcome to Call Log Learner!")
    print("Note: This program currently works only on Windows 10/11 systems with Autopsy 4.21.0.")
    print("-" * 60)

    # Ask if an Autopsy case has been created
    case_created = input("Have you created an Autopsy case? (yes/no): ").strip().lower()
    while case_created not in {"yes", "no"}:
        case_created = input("Please enter 'yes' or 'no': ").strip().lower()

    # Ask for the Autopsy Case Folder Directory
    case_folder_directory = input("Enter your Autopsy Case Folder Directory: ").strip()
    while not os.path.isdir(case_folder_directory):
        print("Invalid directory. Please enter a valid folder path.")
        case_folder_directory = input("Enter your Autopsy Case Folder Directory: ").strip()

    # Store data
    user_data = {
        "Case Created": case_created,
        "Case Folder Directory": case_folder_directory
    }

    # Print the collected data for confirmation
    print("\nCollected Data:")
    for key, value in user_data.items():
        print(f"{key}: {value}")
    
    database_path = os.path.join(case_folder_directory, "autopsy.db")
    if not os.path.isfile(database_path):
        print(f"Could not find the 'autopsy.db' database file at: {database_path}")
        return

    print("\nFound the 'autopsy.db' database. Attempting to retrieve call log information...")
    
    try:
    # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Updated query for retrieving phone numbers from the 'accounts' table
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

    # Display results only for phone numbers starting with '+'
        if results:
            print("\nFiltered Call Log Information (Phone numbers starting with '+'):")
            print("-" * 60)
            for row in results:
                phone_number, file_name, file_path = row
                if str(phone_number).startswith('+'):  # Only display if phone number starts with '+'
                    print(f"Phone Number: {phone_number}")
                    print(f"File Name: {file_name}")
                    print(f"File Path: {file_path}")
                    print("-" * 60)
        else:
            print("\nNo call log information found in the database.")

        # Close the database connection
        conn.close()

    except sqlite3.Error as e:
        print(f"An error occurred while accessing the database: {e}")


    print("\nThank you for using Call Log Learner. Goodbye!")

# Run the program
if __name__ == "__main__":
    call_log_learner()

