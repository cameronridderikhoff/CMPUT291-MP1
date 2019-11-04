import re, sqlite3, sys, getpass, random, datetime, string
import agent_queries as aq
import officer_queries as oq

class menu:
    def __init__(self, connection):
        #initalize class variables
        self.connection = sqlite3.connect(connection)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute(' PRAGMA foreign_keys=ON; ')
        self.connection.commit()
        self.uid = ""        
    # This is the method that we run when we start the system.
    # It prints a welcome message, and starts the main menu.
    # Once the user is done, it performs a commit to ensure the data is saved,
    # and closes the database connection.
    def main(self):    
        print("*************************")
        print("Welcome Mini project 1 system")
        print("*************************")

        # print the menu
        self.main_menu() 

        self.connection.commit()
        self.connection.close()
        return
    
    # The main menu is showd firstly when users open this system
    # This paert will provide 4 different opthins for users to login, sign up and exit.
    def main_menu(self):
        print('Type "a" to login as a Registry Agent')
        print('Type "o" to login as a Traffic Officer')
        print('Type "s" to Sign Up') 
        print('Type "e" to Exit')
        print("*************************")
        Type = input('Please select your option: ') 
        while True:
            if Type.lower() == "a":
                self.a_login()
                return 
            elif Type.lower() == "o":
                self.o_login()  
                return
            elif Type.lower() == "s":
                self.register_user() 
            elif Type.lower() == "e":
                sys.exit()
            else:
                Type = input("Invalid option please try again: ")
    
    # When users choise a at the main menu, they will go the a_login page
    # System will cheeck that if the uid or pwd with the utype is "a" exisit at users table. If not, let users try again or exit. 
    # If uid and pwd matched, show "Welcom (users first name)" and go the a_menu 
    def a_login(self):
        while True:
            self.uid = input("UID: ")
            pwd = getpass.getpass("Password: ")
            self.cursor.execute('SELECT uid FROM users WHERE uid = ?  COLLATE NOCASE;', [(self.uid)])
            result = self.cursor.fetchall()
            if result:
                self.cursor.execute('SELECT * FROM users WHERE pwd = ?  And utype="a" ;' , [(pwd)])  
                results = self.cursor.fetchall()
                if results:
                    for i in results:
                        print("*************************")
                        print("Welcome " + i[3])

                        self.a_menu()
                        return 
                else:
                    print('The password is invalid')
                    while True:
                        uid = input('Please type "o" to try again, type "b" to go back, type "e" to exit: ')
                        if uid.lower() == "e":
                            sys.exit()
                        elif uid.lower()=="b":
                            self.main_menu()
                        elif uid.lower()=="o":
                            self.a_login()       
                        else:
                            print("Invalid option please enter again")
                    
            else:
                print('The UID is invalid')
                while True:
                    choice = input('Please type "o" to try again,type "b" to go back, type "e" to exit: ')
                    if choice.lower() == "e":
                        sys.exit()
                    elif choice.lower()=="b":
                        self.main_menu()
                    elif choice.lower()=="o":
                        self.a_login()       
                    else:
                        print("Invalid option please try again")
    
    # When users choise a at the main menu, they will go the o_login page
    # System will cheeck that if the uid or pwd with the utype is "o" exisit at users table. If not, let users try again or exit. 
    # If uid and pwd matched, show "Welcom (users first name)" and go the o_menu 
    def o_login(self):
        while True:
            self.uid = input("UID: ")
            pwd = getpass.getpass("Password: ")
            self.cursor.execute('SELECT uid FROM users WHERE uid = ?  COLLATE NOCASE;', [(self.uid)])
            result = self.cursor.fetchall()
            if result:
                self.cursor.execute('SELECT * FROM users WHERE pwd=?  And utype="o" ;' , [(pwd)])  
                results = self.cursor.fetchall()
                if results:
                    for i in results:
                        print("*************************")
                        print("Welcome " + i[3])
                        self.o_menu()
                        return 
                else:
                    print('Password is invalid')
                    while True:
                        choice = input('Please type "o" to try again, type "b" to go back, type "e" to exit: ')
                        if choice.lower() == "e":
                            sys.exit()
                        elif choice.lower()=="b":
                            self.main_menu()
                        elif choice.lower()=="o":
                            self.o_login()       
                        else:
                            print("Invalid option please try again")
                    
            else:
                print('UID is invalid')
                while True:
                    choice = input('Please type "o" to try again,type "b" to go back, type "e" to exit: ')
                    if choice.lower() == "e":
                        sys.exit()
                    elif choice.lower()=="b":
                        self.a_menu()
                    elif choice.lower()=="o":
                        self.o_login()       
                    else:
                        print("Invalid option please try again")
        
    
    # When users enter correct uid and pwd, they will go a_menue
    # This part provide 8 options for users
    def a_menu(self):
        print("*************************")
        print("Select a number option from the agents menu")
        print(" 1. Register a birth")
        print(" 2. Register a marriage")
        print(" 3. Renew a vehicle registration")
        print(" 4. Process a bill of sale")
        print(" 5. Process a payment")
        print(" 6. Get a driver abstract")
        print(" 7. Logout ")
        print(" 8. Exit program ")
        print("*************************")
        option = input("your option: ")

        query = aq.agent_queries(self.cursor)

        if option == "1":
            baby_det = query.regex_newborn_details()
            ffname = baby_det[3]
            flname = baby_det[4]
            mfname = baby_det[5]
            mlname = baby_det[6]
            result = False
            while result != True:
                result = query.register_birth(self.cursor, self.uid, baby_det[0], baby_det[1], baby_det[2],
                 ffname, flname, mfname, mlname)
                if result == "m":
                    print("Birth could not be registered, mother does not exist. ")
                    mdetails = query.regex_person_details("the mother's", mfname, mlname)
                    self.cursor.execute("INSERT INTO persons VALUES (?, ?, ?, ?, ?, ?)", (mdetails))
                elif result == "f":
                    print("Birth could not be registered, father does not exist. Would you like to add him?")
                    fdetails = query.regex_person_details("the father's", ffname, flname)
                    self.cursor.execute("INSERT INTO persons VALUES (?, ?, ?, ?, ?, ?)", (fdetails))
                elif result == "u":
                    raise(Exception, "USER IS INVALID")
            self.connection.commit()
            print("Birth Sucessfully Registered.")
            self.a_menu()
        elif option == "2":
            p1fname = input("Please enter the first partner's first name: ")
            p1lname = input("Please enter the first partner's last name: ")
            p2fname = input("Please enter the second partner's first name: ")
            p2lname = input("Please enter the second partner's last name: ")

            result = False
            while result != True:
                result = query.register_marriage(self.cursor, self.uid, p1fname, p1lname, p2fname, p2lname)
                if result == "1":
                    print("Birth could not be registered, the first person does not exist. ")
                    p1details = query.regex_person_details("the first person's", p1fname, p1lname)
                    self.cursor.execute("INSERT INTO persons VALUES (?, ?, ?, ?, ?, ?)", (p1details))
                elif result == "2":
                    print("Birth could not be registered, the second person does not exist. ")
                    p2details = query.regex_person_details("the second person's", p1fname, p1lname)
                    self.cursor.execute("INSERT INTO persons VALUES (?, ?, ?, ?, ?, ?)", (p2details))
                elif result == "u":
                    raise(Exception, "USER IS INVALID")
            self.connection.commit()
            print("Marriage Sucessfully Registered.")
            self.a_menu()
        elif option == "3":
            regno = input("Please enter the registration number of the vehicle you wish to renew: ")
            result = False
            while result != True:
                result = query.renew_vehicle_registration(self.cursor, regno)
                if result == "dne":
                    print("That registration number does not exist.")
                    regno = input("Please enter the registration number of the vehicle you wish to renew: ")
            print("Registration Successfully Updated.")
            self.connection.commit()
            self.a_menu()
        elif option == "4":
            query.process_bill_of_sale(self.cursor)
            self.connection.commit()
            self.a_menu()
        elif option == "5":
            query.process_payment(self.cursor)
            self.connection.commit()
            self.a_menu()
        elif option == "6":
            query.get_driver_abstract(self.cursor)
            self.connection.commit()
            self.a_menu()
        elif option== "7":
            self.main_menu()
        elif option == "8":
            sys.exit()
        else:
            print("invalid input, please try again")
            self.a_menu()
        
       
    # When users enter correct uid and pwd, they will go a_menue
    # This part provide 8 options for users
    def o_menu(self):
        print("*************************")
        print("Select a number option from the officers menu")
        print(" 1. Issue a ticket")    
        print(" 2. Find a car owner.")
        print(" 3. Logout")
        print(" 4. Exit program")
        print("*************************")
        option = input("Your option: ")

        query = oq.officer_queries()
        if option == "1":
            query.issue_ticket(self.cursor)
            self.connection.commit()
            self.o_menu()
        elif option == "2":
            query.find_car_owner(self.cursor)
            self.connection.commit()
            self.o_menu()
        elif option == "3":
            self.main_menu()
        elif option== "4":
            sys.exit()
        else:
            print("Invalid option, please try again")
            self.o_menu()


    # This part will let user sign up an account
    # Users need to enter a new uid and a password which is just only letters and numbers and "_".
    # If the uid and password already exists, user will be asked to create a new one.
    # Users will be asked to enter the personal information like the type,name, city.
    # Then the system will inster the new uid and password with the personal information into the users table.
    def register_user(self):
        create_uid= False
        while create_uid== False:
            uid = input("Please enter a new uid: ")
            if re.match("^[A-Za-z0-9_]*$", uid):
                self.cursor.execute("SELECT uid FROM users WHERE uid = ? COLLATE NOCASE;", [(uid)])
                if self.cursor.fetchall():
                    print("This uid exists. Try another")
                else:
                    create_uid= True
            else:
                print('You can just use letters, numbers or the symbol " _ ", please try again')

        while True:
            pwd = getpass.getpass("please enter your password: ")
            if re.match("^[A-Za-z0-9_]*$", pwd):
                utype=input("Type  'a' for agents, Type 'o' for officers:")
                fname = input("Please enter your first name: ")
                lname = input("Please enter your last name: ")
                city = input("Please enter your city: ")
                data = (uid,pwd,utype,fname,lname,city)
                self.cursor.execute("SELECT * FROM persons WHERE LOWER(fname) = ?  AND LOWER(lname) = ? COLLATE NOCASE;", (fname, lname))
                if (not self.cursor.fetchall()):
                    query = aq.agent_queries(self.cursor)
                    userdetails = query.regex_person_details("your", fname, lname)
                    self.cursor.execute("INSERT INTO persons VALUES (?, ?, ?, ?, ?, ?);", userdetails)
                self.cursor.execute("INSERT INTO  users VALUES (?,?,?,?,?,?);",data)
                break
            else:
                print('You can just use letters, numbers or symbo " _ ",please try again')
        self.connection.commit()
        print("Sign up successfully")
        print("\n\n\n")
    

if __name__ == "__main__":
    m = menu(sys.argv[1])
    m.main()

 
            

    

