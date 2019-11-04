import random, string, sys, datetime, re
import dateutil.parser as date_parser


class officer_queries:
    # This part will generate randomly 3 integers for our ticket no.     
    def generate_tno(self, cursor):
        cursor.execute("SELECT MAX(tno) FROM tickets;")
        return cursor.fetchone()[0] + 1

    # Question 2.1 begins
        
    # Users can view the driver abstract by the regno.
    # If no registration number matched user can will be provided oetions.
    # If registration number matched system will show driver abstract.
    # Users can issue ticket for this driver
    # Insert the new ticket into the tickets table.
    def issue_ticket(self, cursor):
        regno=input("Please enter a registration number to search the informations:" )
        cursor.execute("SELECT r.fname, r.lname, v.make,v.model,v.year,v.color FROM registrations AS r, vehicles AS v  WHERE  regno =? AND r.vin=v.vin COLLATE NOCASE; ",(regno,))   
        results = cursor.fetchall()
        if len(results)==0: 
            t=input('No registration number matched please enter "e" to exit or enter others to try again  :')
            if t.lower() == "e":
                sys.exit()
            else:
                self.issue_ticket(cursor)
                return
                
        else:
            fname=results[0][0]
            lname=results[0][1]
            make=results[0][2]
            model=results[0][3]
            year=results[0][4]
            color=results[0][5]
        print("first name:",fname,"|last name:",lname,"|make:",make,"|model:",model,"|year:",year,"|color:",color)
        print('If you want to issue a ticket please enter "i",if you want to go back please enter "b",if you want to exit pelase enter"e".')
        
        Type=input("Please enter your choice:")
        while Type != "e" and Type != "b" and Type != "i":
            print("invalid input, please try again")
            Type=input("Please enter your choice:")
        if Type.lower() == "e":
            sys.exit()
        elif Type.lower() == "b":
            return
        elif Type.lower() == "i":
            vdate = self.get_valid_date()
            while True:
                #fin will be integer
                #Fin and violation will not be null
                fine_amount=input('Provding a fine amount:')
                if not re.match("^[0-9_]*$", fine_amount):
                    print("The amount should be an integer")
                elif fine_amount=="":
                    print("The amount could not be an null")
                else:
                    while True:
                        violation=input('Providing a a violation text :')
                        if violation=="":
                            print("The violation could not be an null")
                        else:
                            break
                    break 
        cursor.execute("INSERT INTO tickets (tno,regno,fine,violation,vdate) VALUES (?, ?, ?, ?, ?);", 
         (self.generate_tno(cursor), regno, fine_amount, violation, vdate))
        print("Successfully issued ticket") 
        return
    
            
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
    # Question 2.1 ends


    # Question 2.2 begins
    def find_car_owner(self, cursor):
        # Searches database for vehicles based on optional entered data. If there
        # are less than four matching vehicles, all of the data, including owner
        # name, is displayed. If there are four or more vehicles, only the make,
        # model, year, colour, and plate of teh vehicle are displayed.

        info = {'make': '', 'model': '', 'year': '', 'color': '', 'plate': ''}

        query = '''SELECT  make, model, year, color, plate, fname, lname
                FROM    vehicles LEFT OUTER JOIN registrations USING (vin)
                WHERE   make IS NOT NULL --trivial query to allow all others to
                                            --begin with "AND"'''

        bindings = []  # initializes empty list for query bindings

        for key in info:

            # Takes user input
            if key == 'year':
                info[key] = self.check_year()
            else:
                info[key] = input('Enter %s: ' % key).lower()

            # Checks if user chose to exit function
            if info[key] == 'e':
                print('Search cancelled')
                return

            # Updates query with each entered detail
            if info[key]:
                query += '\nAND    %s = ? COLLATE NOCASE' % key
                bindings.append(info[key])

        query += ';'
        cursor.execute(query, bindings)
        results = cursor.fetchall()
        
        outputs = []
        for i in range(len(results)):
            outputs.append('%d. Make: %s, Model: %s, Year: %d, Color: %s, Plate: %s'
                        % (i + 1, results[i][0], results[i][1], results[i][2],
                            results[i][3], results[i][4]))

        # If there are less than four results, add the owner to each vehicle's
        # display
        if len(results) < 4:
            for j in range(len(outputs)):
                if results[j][4] is not None:
                    outputs[j] += ', Owner: %s %s' % (results[j][5], results[j][6])
                else:
                    outputs[j] += ', No Owner'
                    
        [print(k) for k in outputs]
        
        if len(results) >= 4:
            while True:
                selection = input('Select a vehicle: ')
                if selection == 'e':
                    return
                elif not selection.isdigit():
                    print('Error: selection not an integer')
                elif int(selection) not in range(1, len(results)):
                    print('Error: selection out of range')
                elif results[int(selection)][4] is None:
                    print('Car has no owner!')
                else:
                    print('Car #%d owned by %s %s' % (int(selection), results[5],
                                                    results[6]))
        return


    def check_year(self):
        # Validates year input for info dictionary
        # (note year does not have to be entered)

        while True:
            year = input('Enter year: ')

            if year == '':
                return 0
            elif year == 'e':
                return year
            # Makes sure year is either left blank or an integer
            elif not re.match('^([0-9]+)?$', year):
                print('Error: incorrect year format')
            else:
                return int(year)

    # Question 2.2 ends
