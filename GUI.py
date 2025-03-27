"""
This is the code for the Call Log Learner Application!

This app aims to help Students and Novices learn about the Analysis Stage of Digital Forensics.
The app uses a specific Autopsy file to do this, if you don't have this file please email S4102295@glos.ac.uk
The app aims to be used as part of a lesson or multiple lessons on Digital Forensics.
With this aim in mind, hopefully the application will be edited or added too by other uses to improve functionality.

Requirements:
- Python 3.11 or later (may work on earlier versions but not tested)
- Autopsy file named "Dissertation" with the autopsy.db file inside (do not move or rename as could break everything)
"""
import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk, simpledialog
from PIL import Image, ImageTk
import webbrowser

#This function is used to fetch call log info for a selected country code
def fetch_call_log_info():
    selected_country_code = country_code_var.get()
    #Error handling for no country code selected
    if not selected_country_code:
        messagebox.showerror("Error", "Please select a country code first!")
        return

    #Clear any previous output
    result_text.delete("1.0", tk.END)

    #Builds the autopsy database path from the case folder
    case_folder_directory = folder_directory_var.get()
    autopsy_db_path = os.path.join(case_folder_directory, "autopsy.db")

    try:
        #Connects to the Autopsy database
        conn = sqlite3.connect(autopsy_db_path)
        cursor = conn.cursor()

        #Query to retrieve phone numbers from the accounts table with a join on tsk_files
        #Query from tsk_files may not achieve same results as Autopsy does on its own database
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

        #Executes query and fetch results
        cursor.execute(query)
        results = cursor.fetchall()

        #Initialises call_log_info as list
        call_log_info = []

        
        #call_log_into = phone numbers that start with +, file name and file path from accounts database table
        if results:
            for row in results:
                phone_number, file_name, file_path = row
                if str(phone_number).startswith("+" + selected_country_code):
                    call_log_info.append({
                        "Phone Number": phone_number,
                        "File Name": file_name,
                        "File Path": file_path
                    })

        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while accessing the Autopsy database: {e}")

    #If country code is 1 the handle USA code function is called. With current data the USA function is always called
    if selected_country_code == '1'and valid_country_codes:
        handle_usa_code(call_log_info)
    #Error handling for no valid country codes added
    elif not valid_country_codes:
        messagebox.showerror("Error", "Please select a file with valid country codes.")
        return


#For phone numbers starting with 1 (all of them for this data) - the area_codes database is connected too
#The code retrieves phone numbers which are grouped by states and opens a window to filter by state and or area code
def handle_usa_code(call_log_info):
    #Path to the area_codes database
    area_codes_db_path = r"./area_codes.db"

    #Verify the file path - error handling
    if not os.path.isfile(area_codes_db_path):
        messagebox.showerror("Error", "Database file does not exist at the specified path.")
        return

    try:
        #Connects to the area_codes database
        conn = sqlite3.connect(area_codes_db_path)
        cursor = conn.cursor()

        #Query to retrieve states and their area codes from db
        query = """
        SELECT 
            s.state_name, 
            a.area_code 
        FROM 
            States s
        JOIN 
            AreaCodes a ON s.id = a.state_id;
        """

        #Executes the query
        cursor.execute(query)
        results = cursor.fetchall()

        #Groups area codes by state - states can have more than one area code
        state_area_codes = {}
        for state_name, area_code in results:
            if state_name not in state_area_codes:
                state_area_codes[state_name] = []
            state_area_codes[state_name].append(area_code)

        #Filters phone numbers by area code - area code is the 3 digits after the country code
        valid_states = {}
        for state, codes in state_area_codes.items():
            for code in codes:
                if any(info["Phone Number"][2:5] == code for info in call_log_info):
                    valid_states[state] = codes
                    break

        #Closes connection to the area_codes db
        conn.close()

        #Shows notification window 4
        show_notification_window4()

        #Creates window for state and area code selection
        selection_window = tk.Toplevel()
        selection_window.title("Select State and Area Code")
        selection_window.geometry("355x160+1100+150")  #Sets size and position (width x height + x + y)

        #Create and organise frames
        selection_frame = ttk.Frame(selection_window, padding="10")
        selection_frame.pack(fill=tk.BOTH, expand=True)

        #Create labels and comboboxes for state and area code selection
        ttk.Label(selection_frame, text="Select a State:").grid(row=0, column=0, sticky=tk.W, pady=5)
        state_var = tk.StringVar()
        state_combobox = ttk.Combobox(selection_frame, textvariable=state_var, values=list(valid_states.keys()), width=30)
        state_combobox.grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Label(selection_frame, text="Select an Area Code:").grid(row=1, column=0, sticky=tk.W, pady=5)
        area_code_var = tk.StringVar()
        area_code_combobox = ttk.Combobox(selection_frame, textvariable=area_code_var, width=30)
        area_code_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)

        #Button runs function update_area_codes
        state_combobox.bind("<<ComboboxSelected>>", lambda event: update_area_codes(state_var, valid_states, area_code_combobox))

        #Create a button to display filtered phone numbers
        display_button = ttk.Button(selection_frame, text="Display Phone Numbers", command=lambda: display_phone_numbers(state_var, area_code_var, call_log_info, valid_states))
        display_button.grid(row=2, column=0, columnspan=2, pady=10)
       
        #Create a button to display all phone numbers
        display_all_button = ttk.Button(selection_frame, text="Display All Phone Numbers", command=lambda: display_all_phone_numbers(call_log_info))
        display_all_button.grid(row=3, column=0, columnspan=2, pady=10)
    #Error handling for database errors
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while accessing the area_codes database: {e}")
        
#Function runs when the display all phone numbers button is clicked
def display_all_phone_numbers(call_log_info):
    #Deletes any previous output
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "\nAll Phone Numbers:\n")
    result_text.insert(tk.END, "-" * 60 + "\n")

    #Displays all phone numbers within call_log_info
    for index, info in enumerate(call_log_info, start=1):
        result_text.insert(tk.END, f"Phone Number {index}: {info['Phone Number']}\n")
        result_text.insert(tk.END, f"File Name: {info['File Name']}\n")
        result_text.insert(tk.END, f"File Path: {info['File Path']}\n")
    result_text.insert(tk.END, "-" * 60 + "\n")

#Updates area codes to choose from - based on selected state
def update_area_codes(state_var, valid_states, area_code_combobox):
    selected_state = state_var.get()
    if selected_state in valid_states:
        area_code_combobox['values'] = valid_states[selected_state]
    else:
        area_code_combobox['values'] = []

#Displays filtered results based on if a state and/ or area code is selected
def display_phone_numbers(state_var, area_code_var, call_log_info, valid_states):
    #Retrieves selected state and area code
    selected_state = state_var.get()
    selected_area_code = area_code_var.get()
    #Removes any previous output
    result_text.delete("1.0", tk.END)
    #If an area code is selected - the phone numbers are filtered by area code (the three digits after the country code)
    if selected_area_code:
        result_text.insert(tk.END, "\nPhone Numbers associated with the area code:\n")
        result_text.insert(tk.END, "-" * 60 + "\n")
        index = 1
        for info in call_log_info:
            if info["Phone Number"][2:5] == selected_area_code:
                result_text.insert(tk.END, f"Phone Number {index}: {info['Phone Number']}\n")
                result_text.insert(tk.END, f"File Name: {info['File Name']}\n")
                result_text.insert(tk.END, f"File Path: {info['File Path']}\n")
                index += 1
        result_text.insert(tk.END, "-" * 60 + "\n")
    #If just a state is selected - the phone numbers are filtered by state
    elif selected_state in valid_states:
        result_text.insert(tk.END, "\nPhone Numbers associated with the state:\n")
        result_text.insert(tk.END, "-" * 60 + "\n")
        index = 1
        for area_code in valid_states[selected_state]:
            for info in call_log_info:
                if info["Phone Number"][2:5] == area_code:
                    result_text.insert(tk.END, f"Phone Number {index}: {info['Phone Number']}\n")
                    result_text.insert(tk.END, f"File Name: {info['File Name']}\n")
                    result_text.insert(tk.END, f"File Path: {info['File Path']}\n")
                    index += 1
        result_text.insert(tk.END, "-" * 60 + "\n")
    #If user is able to select invalid state or area code - error message
    else:
        result_text.insert(tk.END, "No matching phone details from state or area code selected.\n")

#Loads available country codes from the Autopsy database
#Validates country codes available with country code db (Creator.db)
def load_country_codes():
    show_notification_window3()
    case_folder_directory = folder_directory_var.get()
    #Ensures a folder is selected
    if not case_folder_directory:
        messagebox.showerror("Error", "Please select an Autopsy folder first!")
        return
        #Attempts to connect to the Autopsy database and creator database
    try:
        #Get valid country codes
        autopsy_db_path = os.path.join(case_folder_directory, "autopsy.db")
        creator_db_path = r"./Creator.db"

        #Connect to Autopsy database
        conn_autopsy = sqlite3.connect(autopsy_db_path)
        cursor_autopsy = conn_autopsy.cursor()
        #Query to retrieve phone numbers from the accounts table where account type is 3 (phone numbers)
        cursor_autopsy.execute("SELECT account_unique_identifier FROM accounts WHERE account_type_id = 3;")
        #Builds list of phone numbers - filtering for those that start with a +
        phone_numbers = [pn[0] for pn in cursor_autopsy.fetchall() if pn[0].startswith('+')]
        
        #Creates an empty set for potential codes
        potential_codes = set()
        #For loop - ensures each phone number is checked for a country code
        for pn in phone_numbers:
            #Removes the '+' from the phone number 
            code_part = pn[1:]  
            #Trying for length of 1, 2 and 3 as country codes can be different lengths
            for length in range(1, 4):
                if len(code_part) >= length:
                    #Stores potential country codes
                    potential_codes.add(code_part[:length])

        #Connects to Creator.db
        conn_creator = sqlite3.connect(creator_db_path)
        cursor_creator = conn_creator.cursor()
        #Query to retrieve country codes from the Countries table
        cursor_creator.execute("SELECT phonecode FROM Countries;")
        #Valid codes are stored in a set
        valid_codes = {str(code[0]) for code in cursor_creator.fetchall()}

        #Creates a set where potential codes and valid codes intersect
        global valid_country_codes #Made into global variable for error handling in Handle_USA_Code 
        valid_country_codes = sorted(potential_codes.intersection(valid_codes), key=int)

        if not valid_country_codes:
            messagebox.showerror("Error", "Please select a file with valid country codes.")
            return
        
        #Create new window for country code selection
        code_window = tk.Toplevel()
        code_window.title("Select Country Code")
        #Sets size and position of the window
        code_window.geometry("300x400+500+300")  

        #Creates frame to contain listbox and scrollbar
        list_frame = ttk.Frame(code_window)
        list_frame.pack(padx=10, pady=10)
        #Listbox and scrollbar creation
        listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, width=20, height=15)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        #Inserts all valid country codes into the listbox
        for code in valid_country_codes:
            listbox.insert(tk.END, f"+{code}")

        listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        #Selection button - runs on_code_select function 
        ttk.Button(code_window, text="Select Code", command=lambda: on_code_select(listbox, code_window)).pack(pady=5)
    #Database error handling
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load country codes: {str(e)}")
#Updates the area codes combobox based on the selected state and closes the country code window

def on_code_select(listbox, code_window):
    selected = listbox.get(listbox.curselection())
    country_code_var.set(selected[1:])  
    code_window.destroy()

#Allows user to select the Autopsy folder
def browse_folder():
    folder_path = filedialog.askdirectory(title="Select Autopsy Case Folder")
    if folder_path:
        folder_directory_var.set(folder_path)
        #Runs load_country_codes function
        load_country_codes()

#Closes the main window and shows the intro screen without shutting down program
def back_to_intro():
        global root
        #Destroy the main window
        if root is not None:
            root.destroy()
        #Show the intro screen
        show_intro_screen()

#Main window function - sets up and runs the main window
def show_main_window():
    #Declare global variables
    global folder_directory_var, country_code_var, result_text, root

    #Set up the main window
    root = tk.Tk()
    root.title("Call Log Learner")
    root.geometry("800x700+300+100") 

    #Creates and organize frames
    input_frame = ttk.Frame(root, padding="10")
    input_frame.pack(fill=tk.X)
    result_frame = ttk.Frame(root, padding="10")
    result_frame.pack(fill=tk.BOTH, expand=True)

    #Creates labels, inputs, and buttons for the input frame
    ttk.Label(input_frame, text="Select your Autopsy Case Folder:").grid(row=0, column=0, sticky=tk.W)
    #Entry box for folder directory
    folder_directory_var = tk.StringVar()
    folder_entry = ttk.Entry(input_frame, textvariable=folder_directory_var, width=50)
    folder_entry.grid(row=0, column=1, padx=5, sticky=tk.W)

    #Browse button - runs browse_folder function when clicked
    browse_button = ttk.Button(input_frame, text="Browse", command=browse_folder)
    browse_button.grid(row=0, column=2, padx=5)

    ttk.Label(input_frame, text="Select a Country Code:").grid(row=1, column=0, sticky=tk.W, pady=5)

    #Combobox for country code selection - automatically populated by load_country_codes function
    country_code_var = tk.StringVar()
    country_code_combobox = ttk.Combobox(input_frame, textvariable=country_code_var, width=10)
    country_code_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)

    #Runs fetch_call_log_info function when clicked
    fetch_button = ttk.Button(input_frame, text="Fetch Call Log Info", command=fetch_call_log_info)
    fetch_button.grid(row=2, column=0, columnspan=3, pady=10)

    #Scrolled text widget - displays the results of the call log info
    result_text = scrolledtext.ScrolledText(result_frame, width=70, height=15)
    result_text.pack(fill=tk.BOTH, expand=True)

    #Shows the notification windows 1 and 2
    show_notification_window1()
    show_notification_window2()

    #Shows the navigation bar
    show_navigation_bar()

    #Starts the Tkinter main loop
    root.mainloop()

#Notification window1 - browse button help
def show_notification_window1():
    notification_window1 = tk.Toplevel(root)
    notification_window1.title("Browse Button Help")
    notification_window1.geometry("500x200+900+115")  
    notification_window1.attributes("-topmost", True)  #Makes the window stay on top
    ttk.Label(
        notification_window1,
        text=(
            "<------Here is the browse button                                                                    \n\n\n"
            "Fact: All the information about an Autopsy case is saved witin one database file\n"
            "This db file is called autopsy.db and can be easily explored and looked into using tools such as:\n"
            "Browser for SQLite for browsing the database directly\n"
            "Online tools such as dbdiagram.io for visualising the database\n"
        ),
        justify="center",
        wraplength=450 
    ).pack(pady=20)  

#Notification window2 - what's what?
def show_notification_window2():
    notification_window2 = tk.Toplevel(root)
    notification_window2.title("What's what?")
    notification_window2.attributes("-topmost", True)
    notification_window2.geometry("500x300")  
    
    #Label content
    ttk.Label(
        notification_window2,
        text=(
            "Below this screen is your main window for call log analysis\n\n"
            "On the left you will see the navigation bar\n"
            "This will allow you to bring back helpful notifications that you may have closed\n\n"
            "Please click browse and select the autopsy file previously provided\n"
            "The program will then extract the call log data\n\n"
            "Note for this version of the program that is just the following info:\n"
            "Phone number, File path and File name\n"
        ),
        justify="center",
        wraplength=450  
    ).pack(pady=40)  

    #Force update to calculate window size
    notification_window2.update_idletasks()
    
    #Centre window relative to main window
    main_window_x = root.winfo_x()
    main_window_y = root.winfo_y()
    main_window_width = root.winfo_width()
    main_window_height = root.winfo_height()

    window_width = notification_window2.winfo_width()
    window_height = notification_window2.winfo_height()

    position_right = int(main_window_x + (main_window_width/2) - (window_width/2))
    position_down = int(main_window_y + (main_window_height/2) - (window_height/2))

    #Sets notification window position using coordinates 
    notification_window2.geometry(f"+{position_right}+{position_down}")

#Notification window3 - country code help
def show_notification_window3():
    notification_window3 = tk.Toplevel(root)
    notification_window3.title("Country Code Help")
    notification_window3.attributes("-topmost", True)
    notification_window3.geometry("600x520+750+350")  

    ttk.Label(
    notification_window3,
    text=(
        "This screen is showing you what country codes exist within the autopsy database\n\n"
        "A country code is the first part of a phone number\n"
        "For example, the UK country code is +44 and USA is +1\n"
        "As you can see the only available country code is +1\n\n"
        "We can determine that the call log data within the phone is from the USA\n"
        "When making statements like this in Digital Forensics, we should specify that:\n"
        "• The data suggests the phone is from the US instead of stating: it is a fact this phone is from the USA\n"
        "• Our conclusions are based on the tools and data available\n"
        "In Digital Forensics (DF), we must always be:\n"
        "• Clear and concise in our findings\n"
        "• Compliant with best practices, laws, and regulations\n\n"
        "In England and Wales, DF activities must try to follow follow:\n"
        "• Forensic Science Regulator's (FSR) Codes of Practice and Conduct - FSR Act 2021 \n"
        "• ACPO Good Practice Guide for Digital Evidence - not a law but commonly followed by Police Forces within the UK\n\n"
        "Why standardization matters and how it is applied to call logs:\n"
        "• Country codes (+1 for USA) are followed worldwide, without them the process of calling another country may not work or be extremely complex\n"
        "• DF requires similar standardization for accurate and reliable evidence\n"
        "• While practices vary throughout Digital Forensic Units (DFUs), core principles remain consistent\n\n"
        "Best practice recommendations:\n"
        "• Maintain clear documentation and notes\n"
        "• Use validated tools and methods\n"
        "• Regularly update technical knowledge"
        ),
        justify="center",
        wraplength=550
    ).pack(pady=40)

#Notification window4 - selecting state and area code help
def show_notification_window4():
    notification_window4 = tk.Toplevel(root)
    notification_window4.title("Selecting State and Area Code Help")
    notification_window4.attributes("-topmost", True)
    notification_window4.geometry("355x300+1100+350")  

    ttk.Label(
    notification_window4,
    text=(
        "This Window allows you to browse through the available phone data\n\n"
        "Please select a state to see all phone numbers associated with that state\n"
        "You can select an area code to further filter the phone numbers\n\n"
        "By using the Display Phone numbers button you can see just the filtered results\n"
        "If you want to challenge yourself and try and decipher all the data - click the Display all Phone Numbers button\n\n"
        "To learn more and to complete a task - please click onto the task within the navigation window\n"
        ),
        justify="center",
        wraplength=340
    ).pack(pady=40)

#Notification window5 - task
def show_notification_window5():
    notification_window5 = tk.Toplevel(root)
    notification_window5.title("Task")
    notification_window5.attributes("-topmost", True)
    notification_window5.geometry("950x900+400+50")  

    ttk.Label(
    notification_window5,
    text=(
        "The data displayed within the main window is phone data and has been split up into the following:\n\n"
        "Phone number - which has been enumerated for convenience (phone number 1, phone number 2, etc)\n"
        "File name - the name of the file in which the phone number is stored\n"
        "File location - this is where the phone number is stored according to the tool\n"
        "Task- Find the following phone number: +12066578759 and compare results to this screenshot from Autopsy\n"
        ),
        justify="center",
        wraplength=620
    ).pack(pady=5)

    #Path to the image to display
    image_path = r"./HintArt2.png"
    
    try:
        #Open the image file
        image = Image.open(image_path)
    except Exception as e:
        print("Error opening image:", e)
        return

    #Calculate new dimensions at half the size
    new_width = image.width // 2
    new_height = image.height // 2

    #Resize the image to half its original width and height using lanczos resampling
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)

    #Keep a reference to image - prevents garbage collection
    notification_window5.photo = photo

    #Display the image in a label with 1 pixel of padding
    image_label = ttk.Label(notification_window5, image=photo)
    image_label.pack(pady=1)


    text_label2 = (
        "Task continued - The aim of this task is to be able to use Call Log Learner effectively\n"
        "To do this, you will need to break the phone number down and conduct research\n"
        "The research you will need to do requires you to find out how American phone numbers are structured and formatted\n"
        "This will help you to identify the State and area code details - which can be directly used within the tool\n"
        "The Idea of 'research before you do' is an approach which will help you to think like a Digital Forensic Investigator\n"
        "When completing this task, ensure to make notes. When completed or stuck - click the Task Help Button\n"
    )
    text_label2 = ttk.Label(
        notification_window5,
        text=text_label2,
        justify="center",
        wraplength=620  
    ).pack(pady=5)


#Notification window6 - task help
def show_notification_window6():
    notification_window6 = tk.Toplevel(root)
    notification_window6.title("Task Help")
    notification_window6.attributes("-topmost", True)
    notification_window6.geometry("1300x900+75+50")  
    
    text_label1 = (
       "When researching American phone numbers you should have come across websites such as: "
    )
    text_label1 = ttk.Label(
        notification_window6,
        text=text_label1,
        justify="center",
        wraplength=700  
    )
    text_label1.pack(pady=10)

    urlL = "https://www.worldatlas.com/na/us/area-codes.html"
    urlL_label = tk.Label(notification_window6, text="USA Area Code information", fg="blue", cursor="hand2")
    urlL_label.pack(pady=10)
    urlL_label.bind("<Button-1>", lambda e: webbrowser.open_new(urlL))


    text_label2 = (
        "By doing this research you should be able to identify the following:\n"
        "The phone number was from the state of Washington\n"
        "The area code is the three digits after the country code\n"
        "When making notes, hopefully you were able to identify a discrepancy when compared to Autopsy\n"
        "As you can see from the screenshot below, the file path for both is different \n"
    )

    #Create and pack the second label
    text_label2 = ttk.Label(
        notification_window6,
        text=text_label2,
        justify="center",
        wraplength=700  #Same wrapping as first label
    )
    text_label2.pack(pady=10)



    #Path to the image to display
    image_path = r"./HintArt1.png"
    
    try:
        #Open the image file
        image = Image.open(image_path)
    except Exception as e:
        print("Error opening image:", e)
        return

    #Calculate new dimensions at half the size
    new_width = image.width // 2
    new_height = image.height // 2

    #Resize the image to half its original width and height using lanczos resampling
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)

    #Keeps reference to the image to prevent garbage collection
    notification_window6.photo = photo

    #Display the image in a label with 5 pixels of padding
    image_label = ttk.Label(notification_window6, image=photo)
    image_label.pack(pady=5)


    text_label2 = ttk.Label(
        notification_window6,
        text=(
        "In Digital Forensics it is important to check results and compare with multiple tools\n"
        "To do this, it requires the use of knowledge and research to try and conclude which tool is correct\n"
        "Although, not the main goal, the main point here is to check results and ensure any notes takes reflect the drawbacks of certain tools\n"
        "As a novice you are not expected to know everything - ensure to research and ask questions to come to correct conclusions\n"
        "We recommend you research into the Android 14 database to see where Phone numbers are typically stored\n"
        "If completing this task - update the notes you made"
        ),
        justify="center",
        wraplength=700
    )
    text_label2.pack(pady=10)

#Navigation bar - where buttons to bring back the notifications are
def show_navigation_bar():
    nav_bar = tk.Toplevel()
    nav_bar.title("Navigation")
    root.update_idletasks()  #Ensures all geometry calculations are updated
    #Positions nav bar to the left of the main window
    main_window_x = root.winfo_x()
    main_window_y = root.winfo_y()
    nav_bar.geometry(f"200x700+{main_window_x - 200}+{main_window_y}")

    ttk.Button(
        nav_bar,
        text="Back to the Intro Screen",
        width=30,
        command=back_to_intro #Runs back_to_intro function
    ).pack(pady=10)
    #Buttons to show the notifications and their respective functions
    ttk.Button(nav_bar, text="What's what?", command=show_notification_window2, width=30).pack(pady=10)
    ttk.Button(nav_bar, text="Browse Button Help", command=show_notification_window1, width=30).pack(pady=10)
    ttk.Button(nav_bar, text="Country Code Help", command=show_notification_window3, width=30).pack(pady=10)
    ttk.Button(nav_bar, text="Selecting State & Area Code Help", command=show_notification_window4, width=30).pack(pady=10)
    ttk.Button(nav_bar, text="Task", command=show_notification_window5, width=30).pack(pady=10)
    ttk.Button(nav_bar, text="Task Help", command=show_notification_window6, width=30).pack(pady=10)

#Additional learning screen function - opens a new window with additional learning resources
def show_additional_learning():
    additional_window = tk.Toplevel()
    additional_window.title("Additional Learning")
    additional_window.geometry("600x500")  

    content = (
        "(Yusoff, Ismail and Hassan, 2011) created a Generic Computer Forensic Investigation Model (GCFIM).\n"
        "This model was used to guide the different stages of forensic investigation and helped identify\n"
        "that this tool sits at the Analysis stage.\n"
        "The following stages of this model are Presentation and Post-Process, during which notes are compiled into a forensic report.\n"
        "After this, the investigation is closed, ensuring evidence is kept safe and lessons are learned.\n\n"
        "For a novice, we hope you can evaluate where you might have gone wrong and how to improve next time.\n\n"
        "Pre-Process is defined by (Yusoff, Ismail and Hassan, 2011) as tasks carried out prior to an investigation.\n"
        "Acquisition and Preservation is defined by collecting all relevant data to an investigation and preserving it according to best practices.\n"
        "In Digital Forensics, it's important to be well-prepared. Therefore, we recommend reading the following to prepare yourself."
    )
    ttk.Label(additional_window, text=content, wraplength=380, justify="center").pack(pady=10)

    #URL's to open when clicked
    url1 = "https://www.ibm.com/think/topics/digital-forensics"
    url1_label = tk.Label(additional_window, text="What is Digital Forensics?", fg="blue", cursor="hand2")
    url1_label.pack(pady=10)
    url1_label.bind("<Button-1>", lambda e: webbrowser.open_new(url1))

    url2 = "https://www.sans.org/blog/best-practices-in-digital-evidence-collection/"
    url2_label = tk.Label(additional_window, text="SANS Best Practices in Digital Evidence Collection", fg="blue", cursor="hand2")
    url2_label.pack(pady=10)
    url2_label.bind("<Button-1>", lambda e: webbrowser.open_new(url2))

    url3 = "https://forensiccontrol.com/guides/acpo-guidelines-and-principles-explained/#:~:text=ACPO%20provides%20a%20set%20of%20Guidelines%20for%20Computer,later%20be%20relied%20on%20as%20evidence%20in%20Court."
    url3_label = tk.Label(additional_window, text="The Four Principles of ACPO", fg="blue", cursor="hand2")
    url3_label.pack(pady=10)
    url3_label.bind("<Button-1>", lambda e: webbrowser.open_new(url3))

    url4 = "https://thesecmaster.com/blog/how-to-forensically-analyze-a-disk-using-autopsy/"
    url4_label = tk.Label(additional_window, text="Autopsy Tutorial", fg="blue", cursor="hand2")
    url4_label.pack(pady=10)
    url4_label.bind("<Button-1>", lambda e: webbrowser.open_new(url4))

#Into screen for the application
def show_intro_screen():
    intro_window = tk.Tk()
    intro_window.title("Welcome")
    intro_window.geometry("800x500")

    intro_text = (
        "Welcome to Call Log Learner!\n\n"
        "This application is designed to help learn about the Analysis stage of Digital Forensics!\n\n"
        "To use this application, you don't need any previous knowledge of digital forensics but it certainly will help. "
        "You will see pop-ups – these aim to help with your learning and aim to teach you something you may not know. "
        "If you know everything you see then great!\n\n"
        "In the future, this application aims to be in use as part of a whole lesson on digital forensics, where you would "
        "have previously learnt about two stages:\n"
        "1. Pre-Process\n"
        "2. Acquisition and Preservation\n\n"
        "If you would like to learn about these stages please click onto the learn more button\n"
        "\n\n"
        "Please also note: \n"
        "For this version of Call Log Learner you will need to use a predefined autopsy case that has already been created.\n"
        "If you have not been given access, please contact Jack Marsh at: S4102295@glos.ac.uk\n"
    )

    ttk.Label(intro_window, text=intro_text, wraplength=500, justify="left").pack(pady=20)
    ttk.Button(intro_window, text="Learn More", command=show_additional_learning).pack(pady=10)
    ttk.Button(intro_window, text="Continue", command=lambda: [intro_window.destroy(), show_main_window()]).pack(pady=10)

    intro_window.mainloop()

    

#Show the intro screen
show_intro_screen()