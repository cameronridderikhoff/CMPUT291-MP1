import sqlite3, datetime, sys, re
from dateutil.relativedelta import relativedelta
import dateutil.parser as date_parser

class agent_queries:

    #this method gets a unique registration number from the births table
    def get_unique_birth_regno(self, cur):
        cur.execute("SELECT MAX(regno) FROM births;")
        return cur.fetchone()[0] + 1

    #this method gets a unqiue registration number from the marriages table
    def get_unique_marriage_regno(self, cur):
        cur.execute("SELECT MAX(regno) FROM marriages;")
        return cur.fetchone()[0] + 1

    # Question 1.1 begins

    # This method registers a birth in the births table. It also adds the newborn in the persons table. 
    # births table:
    # births(regno, fname, lname, regdate, regplace, gender, f_fname, f_lname, m_fname, m_lname)
    # persons table:
    # persons(fname, lname, bdate, bplace, address, phone)
    # @param self: the instance of ridderik
    # @param cur: the cursor that allows us to access the database, passed into the method through the main file.
    # @param uid: the user id of the user asking for the insert
    # @param fname: first name of the newborn
    # @param lname: last name of the newborn
    # @param gender: gender of the newborn
    # @param ffname: first name of the father 
    # @param flname: last name of the father
    # @param mfname: first name of the mother
    # @param mlname: last name of the mother
    # @returns: m = mother does not exist, f = father does not exist, u = user done not exist, True = successfully registered
    def register_birth(self, cur, uid, fname, lname, gender, ffname, flname, mfname, mlname):
        mother = self.get_person(cur, mfname, mlname)
        father = self.get_person(cur, ffname, flname)
        user = self.get_user(cur, uid)

        if mother == None:
            return "m"
        elif father == None:
            return "f"
        elif user == None:
            return "u"
        else:
            birth_reg_no = self.get_unique_birth_regno(cur)
            birth_vals = (birth_reg_no, fname, lname, datetime.date.today(), user["city"], gender, ffname, flname, mfname, mlname)
            person_vals = (fname, lname, datetime.date.today(), user["city"], mother["address"], mother["phone"])
            # have to add the statement to persons first, 
            # since births has a foreign key constraint for the newborns first and last name
            cur.execute("INSERT INTO persons VALUES(?, ?, ?, ?, ?, ?);", person_vals)
            cur.execute("INSERT INTO births VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", birth_vals)
            return True
    # Question 1.1 ends

    # Question 1.2 begins

    # This method registers a marriage in the marriages table. 
    # Marriages table:
    # marriages (regno, regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname)
    # @param self: the instance of ridderik
    # @param cur: the cursor that allows us to access the database, passed into the method through the main file.
    # @param uid: the user id of the user asking for the insert
    # @param p1fname: the first name of the first person to be married
    # @param p1lname: the last name of the first person to be married
    # @param p2fname: the first name of the second person to be married
    # @param p2lname: the last name of the second person to be married
    # @returns: 1 = first person does not exist, 2 = second person does not exist, u = user done not exist,
    #           True = successfully registered
    def register_marriage(self, cur, uid, p1fname, p1lname, p2fname, p2lname):
        person1 = self.get_person(cur, p1fname, p1lname)
        person2 = self.get_person(cur, p2fname, p2lname)
        user = self.get_user(cur, uid)

        if person1 == None:
            return "1"
        elif person2 == None:
            return "2"
        elif user == None:
            return "u"
        else:
            marriage_reg_no = self.get_unique_marriage_regno(cur)
            marriage_vals = (marriage_reg_no, datetime.date.today(), user["city"], p1fname, p1lname, p2fname, p2lname)
            cur.execute("INSERT INTO marriages VALUES (?, ?, ?, ?, ?, ?, ?);", marriage_vals)
            return True
    # Question 1.2 ends

    # Question 1.3 begins

    # The user should be able to provide an existing registration number and renew the registration. 
    # The system should set the new expiry date to one year from today's date if the current registration 
    # either has expired or expires today. Otherwise, the system should set the new expiry to one year after 
    # the current expiry date.
    # @param self: the instance of ridderik
    # @param cur: the cursor that allows us to access the database, passed into the method through the main file.
    # @param regno: the registration number of the vehicle to update
    # @returns: dne = registration does not exist, True = update successful
    def renew_vehicle_registration(self, cur, regno):
        cur.execute("SELECT * FROM registrations WHERE regno = (?);", (regno,))
        row = cur.fetchone()
        if row == None:
            return "dne"
        else:
            format_string = "%Y-%m-%d"
            exp_date = datetime.datetime.strptime(row["expiry"], format_string).date()
            if exp_date > datetime.date.today():
                #this code is mostly from https://stackoverflow.com/questions/15741618/add-one-year-in-current-date-python
                new_date = exp_date + relativedelta(years=1)
                new_date_string = datetime.datetime.strftime(new_date, format_string).replace(' 0', ' ')
            else:
                format_string = "%Y-%m-%d"
                new_date = datetime.date.today() + relativedelta(years=1)
                new_date_string = datetime.datetime.strftime(new_date, format_string).replace(' 0', ' ')
            cur.execute("UPDATE registrations SET expiry = (?) WHERE regno = (?);", (new_date_string, regno))
            print("Your vehicle registration expires on: " + new_date_string)
            return True
    # Question 1.3 ends

    # This method gets a user given a unqiue user ID, or uid from the users table.
    # Users table:
    # users(uid, pwd, utype, fname, lname, city)
    # @param self: the instance of ridderik
    # @param cur: the cursor that allows us to access the database, passed into the method through the main file.
    # @param uid: the user id of the user we are looking for
    # @return the user, as a dictionary of key value pairs with the names of the table's rows, or None if the user was not found
    def get_user(self, cur, uid):
        cur.execute("SELECT * FROM users WHERE uid = (?);", (uid,))
        #there will only be one row, if there is any, since uid is the primary key
        #if there is no row, cur.fetchone returns None
        return cur.fetchone()
            
    # This method gets a person from their first and last name, from the persons table.
    # persons table:
    # persons(fname, lname, bdate, bplace, address, phone)
    # @param self: the instance of ridderik
    # @param cur: the cursor that allows us to access the database, passed into the method through the main file.
    # @param fname: first name of the person we are looking for
    # @param lname: last name of the persona we are looking for
    # @return the person as a dictionary of key value pairs with the names of the table's rows, or None if the person was not found
    def get_person(self, cur, fname, lname):
        cur.execute("SELECT * FROM persons WHERE LOWER(fname) = (?) AND LOWER(lname) = (?);", (fname.lower(), lname.lower()))
        #there will only be one row, if there is any, since (firstname, lastname) is the primary key
        #if there is no row, cur.fetchone returns None
        return cur.fetchone()

    # This method ensures all details that are used to create a new person are valid.
    # @param self: the instance of the menu class
    # @param type_of: the type of person we are creating, used to notify the user
    # @param fname: the first name of the person
    # @param lname: the last name of the person
    # @returns: a list containing the details of the person that can be used by another method
    def regex_person_details(self, type_of, fname, lname):
        while (fname == "" or lname == "" 
        and re.match("^[-A-Za-z0-9]*$", fname) and re.match("^[-A-Za-z0-9]*$", lname)):
            print('You can only use letters or, numbers, and you cannot leave the first or last name blank.')
            fname = input("Please enter the %s's first name: " % type_of)
            lname = input("Please enter the %s's last name: " % type_of)

        #dont need to regex check bdate since the get_valid_date() method does this already
        print("Please enter the %s's birthdate: " % type_of)
        bdate = self.get_valid_date()
        regex_check = False
        while not regex_check:
            bplace = input("Please enter the %s's birthplace: " % type_of)
            address = input("Please enter the %s's address: " % type_of)
            phone = input("Please enter the %s's phone number: " % type_of)
            if (re.match("^[A-Za-z0-9_]*$", bplace)
            and  re.match("^[A-Za-z0-9_]*$", address)):
                if re.match("^[0-9-]*$", phone):
                    regex_check = True
                else:
                    print('You can only use numbers or the symbol " - " in the phone number, please try again')

            else:
                print('You can only use letters, numbers or the symbol " _ " in the birthplace and address, please try again')
        return [fname, lname, bdate, bplace, address, phone]

    # This method does a regex check on all the details that are inputted by the user in order 
    # to register a birth.
    # @param self: the instance of the menu class
    # @returns: a list of the details needed to create a newborn
    def regex_newborn_details(self):
        regex_check = False
        while not regex_check:
            fname = input("Please enter the newborn's first name (Only letters and numbers are allowed): ")
            regex_check = re.match("^[-A-Za-z0-9]*$", fname)
        regex_check = False    
        while not regex_check:
            lname = input("Please enter the newborn's last name (Only letters and numbers are allowed): ")
            regex_check = re.match("^[-A-Za-z0-9]*$", lname)
        regex_check = False
        while not regex_check:
            gender = input("Please enter the newborn's gender (Only letters and numbers are allowed): ")
            regex_check = re.match("^[A-Za-z0-9_]*$", gender)
        regex_check = False    
        while not regex_check:
            mfname = input("Please enter the mother's first name (Only letters and numbers are allowed): ")
            regex_check = re.match("^[-A-Za-z0-9]*$", mfname)
        regex_check = False    
        while not regex_check:
            mlname = input("Please enter the mother's last name (Only letters and numbers are allowed): ")
            regex_check = re.match("^[-A-Za-z0-9]*$", mlname)
        regex_check = False    
        while not regex_check:
            ffname = input("Please enter the father's first name (Only letters and numbers are allowed): ")
            regex_check = re.match("^[-A-Za-z0-9]*$", ffname)
        regex_check = False    
        while not regex_check:
            flname = input("Please enter the father's last name (Only letters and numbers are allowed): ")
            regex_check = re.match("^[-A-Za-z0-9]*$", flname)
        return [fname, lname, gender, ffname, flname, mfname, mlname]

    # This method gets the user to input a date in the format "YYYY-MM-DD", and performs a regex check,
    # as well as ensures that the date is valid (Eg. the system will not allow Feb 31)
    # @param self: the instance of the menu class
    # @returns: a date, if the user enters nothing, it will return the current date, otherwise, it will return a valid date
    def get_valid_date(self):
        while True:
            vdate=input('If you want to use the current date, please press enter, otherwise please enter a date with the format "YYYY-MM-DD": ')
            format_string = '%Y-%m-%d'
            if vdate=="":
                vdate=datetime.datetime.now().strftime(format_string)
                return vdate
            elif not re.match("^[0-9-]*$", vdate):
                print("The date can only contain numbers")                
            elif len(vdate.split("-")) < 3:
                    print('Invalid format')
            else:
                try:
                    return date_parser.parse(vdate)
                except:
                    print("This date does not exist, please try again.")

    # Question 1.4 begins
    def process_bill_of_sale(self, cursor):
        # Updates the registration table in the database with information for the 
        # sale of a car

        print("Enter sale information or 'e' to exit")

        # Dictionary used for easier passage of variables into functions
        info = {'vin': '', 'current': '', 'new': '', 'plate': ''}

        # Takes user input for each piece of information for the sale until all
        # information has been entered or the user exits the function
        while not self.check_vin(cursor, info):
            pass
        while 'e' not in info.values() and not self.check_current(cursor, info):
            pass
        while 'e' not in info.values() and not self.check_new(cursor, info):
            pass
        while 'e' not in info.values() and not self.check_plate(cursor, info):
            pass
        
        # Exits the function if the user cancels the sale
        if 'e' in info.values():
            print('Transaction cancelled')
            return

        # Updates expiry date of seller's registration
        # COLLATE NOCASE used in queries for case-insensitivity
        cursor.execute('''UPDATE    registrations
                        SET       expiry = date('now')
                        WHERE     vin = ? COLLATE NOCASE;''', (info['vin'],))

        # Finds highest registration number so new number can be unique
        cursor.execute('SELECT MAX(regno) FROM registrations;')

        # Prepares data to be passed into table
        inserts = (cursor.fetchone()[0] + 1, info['plate'], info['vin'],
                info['new'].split()[0], info['new'].split()[1])

        # Passes data into table
        cursor.execute('''INSERT INTO registrations VALUES
                        (?,date('now'),date('now', '+1 years'),?,?,?,?);''',
                    inserts)

        print('Sale recorded!')

    def check_vin(self, cursor, info):
        # Validates user input for VIN and updates info dictionary

        vin = input('Enter VIN: ')
        cursor.execute('''SELECT vin FROM registrations WHERE LOWER(vin) = ? COLLATE NOCASE;''', (vin.lower(),))

        if vin == 'e':
            info['vin'] = vin
            return True

        # Ensures VIN has been entered
        elif not len(vin) >= 1:
            print('Error: VIN not entered')
            return False
        else:
            row = cursor.fetchone()
            if row == None:
                print('Error: vehicle not in database')
                return False
            info['vin'] = row[0]
            return True


    def check_current(self, cursor, info):
        # Validates user input for the vehicle's current owner and updates info
        # dictionary

        current = input('Enter name of current owner: ')
        cursor.execute('''SELECT	fname, lname
                        FROM	    registrations
                        WHERE     vin = ? COLLATE NOCASE
                        ORDER BY  regdate DESC
                        LIMIT	    1;''', (info['vin'],))
        real_current = cursor.fetchone()

        if current == 'e':
            info['current'] = current
            return True

        # Ensures two names of only alphabetical characters
        elif not re.match('^[-A-Za-z0-9]+ [-A-Za-z0-9]+$', current):
            print('Error: incorrect name format')
            return False

        # compare the entered name and the vehicle's corresponding name
        elif (real_current[0].lower(), real_current[1].lower()) !=\
            (current.split()[0].lower(), current.split()[1].lower()):
            print('Error: wrong owner')
            return False

        else:
            info['current'] = current
            return True


    def check_new(self, cursor, info):
        # Validates user input for the vehicle's new owner and updates info
        # dictionary    

        new = input('Enter name of buyer: ')

        # get all names from persons to check for new owner's name
        cursor.execute('''SELECT fname, lname FROM persons WHERE LOWER(fname) = ? AND LOWER(lname) = ? COLLATE NOCASE;''',
         [new.split()[0].lower(), new.split()[1].lower()])

        if new == 'e':
            info['new'] = new
            return True

        # Ensures two names of only alphabetical characters
        elif not re.match('^[-A-Za-z0-9]+ [-A-Za-z0-9]+$', new):
            print('Error: incorrect name format')
            return False

        elif new.lower() == info['current'].lower():
            print('Error: cannot sell to self')
            return False

        else:
            row = cursor.fetchone()
            if row == None:
                print('Error: buyer not in database')
                return False
            info['new'] = "" + row[0] + " " + row[1]
            return True


    def check_plate(self, cursor, info):
        # Validates user input for the vehicle's plate and updates info dictionary    

        plate = input('Enter plate number: ')
        cursor.execute('SELECT plate FROM registrations WHERE vin = ?'
                    'COLLATE NOCASE;',
                    (info['vin'],))

        if plate == 'e':
            info['plate'] = plate
            return True

        elif not len(plate) >= 1:
            print('Error: plate not entered')
            return False

        elif plate.lower() not in [i[0].lower() for i in cursor.fetchall()]:
            print('Error: incorrect plate')
            return False

        else:
            info['plate'] = plate
            return True
    # Question 1.4 ends


    # Question 1.5 begins
    def process_payment(self, cursor):
        # Processes a payment for a ticket. If the ticket has already been paid in
        # full or the payment would go over the ticket's value, the payment is
        # rejected.

        print("Enter sale information or 'e' to exit")

        info = {'tno': '', 'payment': ''}

        while not self.check_tno(cursor, info):
            pass
        while 'e' not in info.values() and not self.check_payment(cursor, info):
            pass

        if 'e' in info.values():
            print('Transaction cancelled')
            return

        cursor.execute("INSERT INTO payments VALUES (?, datetime('now'), ?);",
                    (info['tno'], info['payment']))
        print('Payment recorded!')


    def check_tno(self, cursor, info):
        # Validates user input for the ticket number, ensuring the number has been
        # correctly entered and that its corresponding ticket is in the database

        tno = input("Enter ticket number: ")

        cursor.execute('SELECT tno FROM tickets;')
        tickets = [i[0] for i in cursor.fetchall()]

        if tno == 'e':
            info['tno'] = tno
            return True

        elif not re.match('^[0-9]+$', tno):
            print('Error: incorrect ticket number format')
            return False

        elif int(tno) not in tickets:
            print('Error: ticket number does not exist')
            return False

        else:
            info['tno'] = int(tno)
            return True


    def check_payment(self, cursor, info):
        payment = input('Enter payment amount: ')

        cursor.execute('''SELECT  fine, SUM(amount)
                        FROM    tickets LEFT OUTER JOIN payments USING (tno)
                        WHERE   tno = ?
                        GROUP BY fine;''', (info['tno'],))

        # account for null values for tickets that have had no payments made
        ticket = [i for i in cursor.fetchone()]
        if ticket[1] is None:
            ticket[1] = 0

        if payment == 'e':
            info['payment'] = payment
            return True
        elif not re.match('^[0-9]+$', payment):
            print('Error: incorrect payment format')
            return False
        elif int(payment) + ticket[1] > ticket[0]:
            print('Payment too high! Current amount paid for this ticket: $' + str(ticket[1]) +' out of $' + str(ticket[0]))
            return False
        else:
            info['payment'] = int(payment)
            return True
    # Question 1.5 ends


    # Question 1.6 begins

    # This part will provide a driver abstract by drivers' name with nocase
    # Show number of tickets, the number of demerit notices, the total number of demerit points received both within the past two years and within the lifetime.
    # Users can view the 5 tickets informations which ordered from the latest to the oldest or every ticket informations
    def  get_driver_abstract(self, cursor):
        print("You are able to enter a first name and a last name to get a driver abstract.") 
        fname=input("Please enter a first name: ")
        lname=input("Please enter a last name: ")
        cursor.execute(" SELECT fname,lname FROM registrations  Where fname= ?  COLLATE NOCASE AND  lname= ? COLLATE NOCASE;",[(fname),(lname)])
        results = cursor.fetchall()
        if  len(results)==0 : 
            print("This person does not have any registrations.")
            t=input('Please enter "e" to go back to the agent menu or enter others to try again: ')
            if t.lower() == "e":
                return
            else:
                self.get_driver_abstract(cursor)           
            
        else:
            cursor.execute("SELECT count(t.tno) FROM tickets t,registrations r Where t.regno=r.regno AND fname= ?  COLLATE NOCASE And lname= ?  COLLATE NOCASE;",[(fname),(lname)])
            results1=cursor.fetchall()
             
            cursor.execute("SELECT fname,lname,COUNT(*) FROM demeritNotices Where fname= ? COLLATE NOCASE And lname= ? COLLATE NOCASE ;" ,[(fname),(lname)])
            results2 = cursor.fetchall()
            # Demerit points received within the past two years 
            cursor.execute("SELECT fname,lname,sum(points) FROM demeritNotices  Where fname= ?  COLLATE NOCASE And lname= ? COLLATE NOCASE AND DATE(ddate) >=DATE('now', '-2 year') ;", [(fname),(lname)])
            results3 = cursor.fetchall()
            # Demerit points received within the life time
            cursor.execute("SELECT fname,lname,sum(points) FROM demeritNotices  Where fname= ?  COLLATE NOCASE And lname= ?  COLLATE NOCASE;", [(fname),(lname)])
            results4 = cursor.fetchall()
            
            fname=results[0][0]
            lname=results[0][1]
            number_tickets=results1[0][0]
            number_demerit=results2[0][2]
            number_points_2=results3[0][2]
            number_points_l=results4[0][2]
            if number_tickets==None:
                number_tickets='0'
            if number_demerit==None:
                number_demerit='0'        
            if number_points_2==None:
                number_points_2='0'
            if  number_points_l==None:
                number_points_l='0'        
                    
            print("first name:",fname,"|last name:",lname,"| number of tickets:",number_tickets,"|number of demerit:",number_demerit,"| total number of demerit points received within the past two years:",number_points_2,"| total number of demerit points received both within the lifetime:",number_points_l)    
            while True:
                option=input('Enter "y" to view  '+fname+ '  tickets , or enter "e" will go back to the agent menu, or enter "t" to view another driver abstract:')
                if option.lower()=="e":
                    return
                elif option.lower()=="t":
                    self.get_driver_abstract(cursor)
                    return
                elif option.lower()=="y":
                    if number_tickets==0:
                        while True:
                            q=input('This driver does not have any ticket,enter "e" will go back to the agent menu,or enter others to view another driver abstract: ')
                            if q.lower()=="e":
                                return
                            else :
                                self.get_driver_abstract(cursor)
                                return
                          
                    else:
                        # Show the top 5 tickets informations to users 
                        cursor.execute("SELECT t.tno,t.violation,t.vdate,t.fine,r.regno,v.make,v.model FROM tickets t,registrations r,vehicles v WHERE r.fname =? AND r.lname =? AND r.regno = t.regno AND r.vin = v.vin ORDER BY t.vdate DESC limit 5;",[(fname),(lname)])  
                        tickets=cursor.fetchall()
                        print("\n")
                        print("These are the Top 5  tickets which ordered from the latest to the oldest")
                        print("\n")
                        for i in tickets:  
                            print("Tno:%d|violation:%s |vdate:%s|fine:%d|regno:%d|make:%s|model:%s"%(i[0],i[1],i[2],i[3],i[4],i[5],i[6]))
                       
                        while True:
                            x=input('Enter "a" to view all tickets, or enter "e" will go back to the agent menu, or enter "t" to view another driver abstract:')
                            if x.lower()=="e":
                                return
                            elif x.lower()=="t":
                                self.get_driver_abstract(cursor)
                            elif x.lower()=="a":
                                # Show the all tickets informations to users 
                                cursor.execute("SELECT t.tno,t.violation,t.vdate,t.fine,r.regno,v.make,v.model FROM tickets t,registrations r,vehicles v WHERE r.fname =? AND r.lname =? AND r.regno = t.regno AND r.vin = v.vin ORDER BY t.vdate DESC ;",[(fname),(lname)])  
                                ticket=cursor.fetchall()
    
                                for i in ticket:  
                                    print("Tno:%d|violation:%s |vdate:%s|fine:%d|regno:%d|make:%s|model:%s"%(i[0],i[1],i[2],i[3],i[4],i[5],i[6]))
                                break
                            else:
                                print("Violate option")
                            
                        print("Retrieved driver abstract over")
                        return    
                
                else:
                    print("Violate option")     
    # Question 1.6 ends