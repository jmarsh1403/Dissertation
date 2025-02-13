import os
import sqlite3

def call_log_learner():
    print("Welcome to Call Log Learner!")
    print("Note: This program currently works only on Windows 10/11 systems with Autopsy 4.21.0.")
    print("-" * 60)

    # Ask for the Autopsy Case Folder Directory
    case_folder_directory = input("Enter your Autopsy Case Folder Directory: ").strip()
    case_folder_directory = r"C:\Users\Jack\OneDrive - University of Gloucestershire\Diss\Diss Assignment\Autopsy\Dissertation"
    while not os.path.isdir(case_folder_directory):
        print("Invalid directory. Please enter a valid folder path.")
        case_folder_directory = input("Enter your Autopsy Case Folder Directory: ").strip()

    # Store data
    user_data = {
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

    # Retrieve phone numbers from the Autopsy database
    print("\nRetrieving phone numbers from the Autopsy database...")

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

        # Debugging: Print the extracted digits
        print("\nExtracted First Three Digits:")
        print(first_three_digits)
        print("\nExtracted First Two Digits:")
        print(first_two_digits)
        print("\nExtracted First Digit:")
        print(first_digit)

        # Close the Autopsy database connection
        conn_autopsy.close()

    except sqlite3.Error as e:
        print(f"An error occurred while accessing the Autopsy database: {e}")
        return

    # Retrieve valid country codes from the Creator database
    print("\nRetrieving valid country codes from the Creator database...")

    try:
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

    except sqlite3.Error as e:
        print(f"An error occurred while accessing the Creator database: {e}")
        return

    # Compare and display the valid country codes found in the Autopsy database
    valid_autopsy_country_codes = first_three_digits.intersection(valid_country_codes)
    valid_autopsy_country_codes.update(first_two_digits.intersection(valid_country_codes))
    valid_autopsy_country_codes.update(first_digit.intersection(valid_country_codes))

    if valid_autopsy_country_codes:
        print("\nValid Country Codes from Autopsy Database:")
        print("-" * 60)
        for code in valid_autopsy_country_codes:
            print(f"Country Code: {code}")
        print("-" * 60)
    else:
        print("\nNo valid country codes found in the Autopsy database.")
        return

    # Ask the user to input a country code from the valid country codes
    while True:
        country_code = input("\nEnter a country code from the valid country codes: ").strip()
        if country_code in valid_autopsy_country_codes:
            break
        print("Invalid country code entered. Please try again.")

    # Retrieve and filter phone numbers based on the user-provided country code
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

    # Handle USA-specific area codes if the country code is 1
    if country_code == '1':
        handle_usa_code()

    print("\nThank you for using Call Log Learner. Goodbye!")

def handle_usa_code():
    # Path to the area_codes database
    area_codes_db_path = r"C:\Users\Jack\OneDrive - University of Gloucestershire\Diss\Diss Assignment\Dissertation\area_codes.db"

    # Verify the file path
    if not os.path.isfile(area_codes_db_path):
        print("Database file does not exist at the specified path.")
        return False

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
            print("\nStates and their Area Codes:")
            print("-" * 60)
            for state_name, area_codes in state_area_codes.items():
                area_codes_str = ", ".join(area_codes)
                print(f"State: {state_name}, Area Codes: {area_codes_str}")
            print("-" * 60)
        else:
            print("\nNo states or area codes found in the database.")

        # Close the area_codes database connection
        conn.close()

    except sqlite3.Error as e:
        print(f"An error occurred while accessing the area_codes database: {e}")

    return True

# Run the program
if __name__ == "__main__":
    call_log_learner()