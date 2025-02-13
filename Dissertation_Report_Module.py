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


    match_found = False

    while not match_found:
        country_code_input = input("Enter the country code (e.g., 44 for UK, 1 for USA): ").strip()

        if not country_code_input.isdigit():
            print("Please enter a valid number.")
            continue

        # Convert the input to an integer after confirming it's a digit
        country_code = int(country_code_input)

        if country_code == 1:
            if handle_usa_code():  # If USA is handled, exit the function
                return  

        for code in phone_codes:
            if country_code == code[0]:
                match_found = True
                break

        if match_found:
            print("Valid country code")
        else:
            print("Invalid country code")


        

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
                if str(phone_number).startswith(f'+{country_code}'):
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
