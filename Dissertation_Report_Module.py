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
    
    # Define database paths
    autopsy_db_path = os.path.join(case_folder_directory, "autopsy.db")
    creator_db_path = r"C:\Users\Jack\OneDrive - University of Gloucestershire\Diss\Diss Assignment\Dissertation\Creator.db"

    # Check if autopsy.db exists
    if not os.path.isfile(autopsy_db_path):
        print(f"Could not find the 'autopsy.db' database file at: {autopsy_db_path}")
        return

    # Now retrieve phone codes from the Creator database
    print("\nRetrieving phone codes from the Creator database...")

    try:
        # Connect to the Creator database
        conn_creator = sqlite3.connect(creator_db_path)
        cursor_creator = conn_creator.cursor()

        # Query to get all phone codes
        phone_code_query = "SELECT phonecode FROM Countries;"

        # Execute the query
        cursor_creator.execute(phone_code_query)
        phone_codes = cursor_creator.fetchall()

        # Display the phone codes
        if phone_codes:
            print("\nPhone Codes from 'Countries' Table:")
            print("-" * 60)
            for code in phone_codes:
                print(f"Phone Code: {code[0]}")
            print("-" * 60)
        else:
            print("\nNo phone codes found in the database.")

        # Close the Creator database connection
        conn_creator.close()

    except sqlite3.Error as e:
        print(f"An error occurred while accessing the Creator database: {e}")

    # Ask the user for a country code
    match_found = False

    while not match_found:
        country_code_input = input("Enter the country code (e.g., 44 for UK, 1 for USA): ").strip()

        if not country_code_input.isdigit():
            print("Please enter a valid number.")
            continue

        # Convert the input to an integer after confirming it's a digit
        country_code = int(country_code_input)

        for code in phone_codes:
            if country_code == code[0]:
                match_found = True
                break

        if match_found:
            print("It Matches")
        else:
            print("It does not match")

    try:
        # Connect to the Autopsy database
        conn = sqlite3.connect(autopsy_db_path)
        cursor = conn.cursor()

        # Query for retrieving phone numbers from the 'accounts' table
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

        # Filter results based on the user-provided country code
        if results:
            print(f"\nFiltered Call Log Information (Phone numbers starting with '+{country_code}'):") 
            print("-" * 60)
            for row in results:
                phone_number, file_name, file_path = row
                if str(phone_number).startswith(f'+{country_code}'):  # Only display if phone number starts with the country code
                    print(f"Phone Number: {phone_number}")
                    print(f"File Name: {file_name}")
                    print(f"File Path: {file_path}")
                    print("-" * 60)
        else:
            print("\nNo call log information found in the database.")

        # Close the Autopsy database connection
        conn.close()

    except sqlite3.Error as e:
        print(f"An error occurred while accessing the Autopsy database: {e}")

    print("\nThank you for using Call Log Learner. Goodbye!")

# Run the program
if __name__ == "__main__":
    call_log_learner()