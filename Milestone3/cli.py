import cmd2
from sqlalchemy import create_engine
import datetime
import pymysql
import argparse
import re
from tabulate import tabulate

hostname="bt62qaouwjhojwysyy5p-mysql.services.clever-cloud.com"
dbname="bt62qaouwjhojwysyy5p"
uname="upayknm2h80sfwra"
pwd="UWON0IfrCL2B4uxVcfcX"

try: 
    connection = pymysql.connect(host= hostname, user= uname, passwd= pwd, db= dbname)
    cursor=connection.cursor()

    # engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
    #             .format(host=hostname, db=dbname, user=uname, pw=pwd))
except Exception as e:
    print(e)
    print("Problem connecting to the database server")

def check_email(email):

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
 
    else:
        return False

def check_date(date):
    format = "%Y-%m-%d"
    try:
        if (datetime.datetime.strptime(date, format) <= datetime.datetime.today()):
            return True
        else:
            print("Date can not be in the future!")
            return False
    except ValueError:
        print("This is an incorrect date format. It should be YYYY-MM-DD")
        return False

def check_gender(gender):
    if (gender in ['m', 'M', 'Male', 'male']):
        gender = 'M'
    elif (gender in ['f', 'F', 'female', 'Female']):
        gender = 'F'
    else: 
        return 'X'

    return gender

def check_user(username):
    exists = f"SELECT COUNT(*) FROM User WHERE User.username = '{username}'"
    cursor.execute(exists)
    result = cursor.fetchone()[0]
    return result

def get_official_name(name):
    count = f"SELECT COUNT(*) FROM Country C WHERE C.name LIKE '%{name}%'"
    cursor.execute(count)
    count = cursor.fetchall()[0]
    if(int(count[0]) != 1):
        return 'X'

    o_name = f"SELECT C.name FROM Country C WHERE C.name LIKE '%{name}%'"
    cursor.execute(o_name)
    o_name = cursor.fetchone()[0]
    return o_name

def print_country(country_data):
    half1 = [country_data[:6]]
    half2 = [country_data[6:]]

    half1 = tabulate(half1, headers=['Official Name', 'Calling code', 'Driving side', 'Gov type', 'Continent', 'Legislature'])
    half2 = tabulate(half2, headers=['Population', 'Area', 'Water%', 'GDP PP', 'GDP Nominal', 'Gini Index', 'HDI', 'Covid Cases', 'Vaccines'])
    
    print(140*'*')
    print(65*' ', 'New Entry!', 65*' ')
    print(140*'*')
    print(half1)
    print(140*'.')
    print(half2)
    # print(120*'*')
    # print(55*' ', 'New Entry!', 55*' ')
    # print(120*'*')
CMD_CAT_APP_MGMT = 'WGS tools'       
class wgs(cmd2.Cmd):
    def __init__(self):
        
        cmd2.Cmd.__init__(self)
        self.prompt = 'wgs>>'
        print("Welcome to WGS Shell!\n"\
            "This shell will allow you to access information from the WGS database.\n"\
            "To know how to use the shell please wirte ? or help for help\n"\
            "Enjoy!")
    
    def do_createUser(self, args):
        """
        createUser adds a new user to the database
        To use createUser, enter the arguments in the follwing comma seperated format:
        createUser <username>,<email>,<gender>,<birthdate>
        Arguments:
        - username: should be a unique user name that will be used for adding reviews
        - email: should be in the format abc@xyz.asd
        - gender: enter M for male and F for female
        - birthdate: should be a valid date in the form YYYY-MM-DD 
        """
        if (len(args.split(',')) < 4):
            print("To use createUser, enter the arguments in the follwing comma seperated format:\
                    \ncreateUser <username>,<email>,<gender>,<birthdate>")
            return

        username, email, gender, birthdate = args.split(',')

        if(check_gender(gender) == 'X'):
            print ("Please enter your gender correctly (M or F)")
            return
        

        if(not check_date(birthdate)):
            return

        if(not check_email(email)):
            print("Please enter a valid email!")
            return

        if(check_user(username)):
            print("Username already exists! Please choose another username.")
            return

        addUser_query = f"INSERT INTO User VALUES ('{username}','{email}','{gender}','{birthdate}')"
        cursor.execute(addUser_query)
        connection.commit()
        #self.poutput('App')
    
    def do_addReview(self, args):
        """
        addReview adds a new review about a specific country to the database
        To use addReview, enter the arguments in the follwing comma seperated format:
        addReview <username>,<country_name>,<travel_date>,<rating>,<txt_review>
        Arguments:
        - username: should be a user name that already exists in the database
        - country_name: the country to be reviewd
        - travel_date: should be a valid date in the form YYYY-MM-DD
        - rating: enter a value between 1 and 10
        - txt_review: add a brief review about the country
        """
        if (len(args.split(',')) < 5):
            print("To use addReview, enter the arguments in the follwing comma seperated format:\
                    \naddReview <username>,<country_name>,<travel_date>,<rating>,<txt_review>")
            return
        username, country_name, travel_date, rating, txt_review = args.split(',')

        if(not check_date(travel_date)):
            return

        if (int(rating) > 10 or int(rating) < 1):
            print("Rating should be between 1 and 10")
            return
        
        official_name = get_official_name(country_name)
        if (official_name == 'X'):
            print("Country name is incorrect!")
            return

        if (not check_user(username)):
            print("To add a review you must be a user! Please create a user to add your review.")
            return 

        addReview_query = f"INSERT INTO User_review VALUES ('0', '{travel_date}','{rating}','{txt_review}','{username}', '{official_name}')"
        cursor.execute(addReview_query)
        connection.commit()
        #self.poutput('App')
    
    def do_countriesWithLegislature(self, legislature):
        """
        countriesWithLegislature is used to show all the countries that have a specific legislature.
        To use countriesWithLegislature, enter the arguments in the follwing format:
        countriesWithLegislature <legislature>
        Arguments:
        - legislature: the type of legislature to search for
        """
        legislature_query = f"SELECT C.name FROM Country C WHERE C.legislature LIKE '%{legislature}%'"
        cursor.execute(legislature_query)
        results = cursor.fetchall()
        if not results:
            print("There exist no countries with such legislature!")
            return

        for x in results:
            print(x[0])
        #self.poutput('App')
    
    def do_countryOfCapital(self, capital):
        """
        countryOfCapital is used to identify the country of a given capital.
        To use countryOfCapital, enter the arguments in the follwing format:
        countryOfCapital <capital>
        Arguments:
        - capital: the capital name to search for in the database
        """
        countryOfCapital_query = f"SELECT C.country_name FROM Capital C WHERE C.name LIKE '%{capital}%'"
        cursor.execute(countryOfCapital_query)
        results = cursor.fetchall()
        if not results:
            print("There exist no countries associated with this capital!")
            return
        
        for x in results:
            print(x[0])
        #self.poutput('App')
    
    def do_countryWithPhoneNo(self, phone_number):
        """
        countryWithPhoneNo is used to identify the country for a given phone number.
        To use countryWithPhoneNo, please enter the phone number in the follwing space seperated format:
        countryWithPhoneNo <calling_code> <phone_number>
        Arguments:
        - calling_code: the calling code of a specific country (in the form +000)
        - phone_number: the reset of the phone number
        """
        calling_code = phone_number.split()[0]
        if len(calling_code) > 5:
            calling_code = calling_code[:3]

        callingCode_query = f"SELECT C.name FROM Country C WHERE C.calling_code LIKE '%{calling_code}%'"
        cursor.execute(callingCode_query)
        results = cursor.fetchall()
        if not results:
            print("There exist no countries associated with this phone number!")
            return

        for x in results:
            print(x[0])
        #self.poutput('App')

    def do_countryByDrivingside(self, driving_side):
        """
        countryByDrivingside is used to show all the countries who drive on the right vs. on the left
        Usage:
        countryByDrivingside <driving side>
        Arguments:
        - driving side: can be 'left', 'Left', 'l', 'L' for left, or 'right', 'Right', 'r', 'R' for right
        """
        if driving_side in ['left', 'Left', 'l', 'L']:
            driving_side = 'l'
        elif driving_side in ['right', 'Right', 'r', 'R']:
            driving_side = 'r'
        else:
            print(f"Invalid driving side {driving_side}!")
            return
        
        drivingside_query = f"SELECT C.name FROM Country C WHERE C.driving_side = '{driving_side}'"
        cursor.execute(drivingside_query)
        results = cursor.fetchall()
        if not results:
            print("There exist no countries associated with this driving side!")
            return

        for x in results:
            print(x[0])
        #self.poutput('App')
    
    def do_countryInfo(self, Cname):
        """
        countryInfo is used to get all the data about a specific country
        Usage:
        countryInfo <country_name> 
        Arguments:
        - country_name: the name of the country to be searched (You can enter Egy for Egypt)
        """
        Cinfo_query = f"SELECT * FROM Country C WHERE C.name LIKE '%{Cname}%'"
        cursor.execute(Cinfo_query)
        results = cursor.fetchall()
        if not results:
            print("Country name does not exist!")
            return

        # results = tabulate(results, headers=['Name', 'Calling code', 'Driving side', 'Gov type', 'Continent', 'Legislature'\
        #                     'Population', 'Area', 'Water%', 'GDP PP', 'GDP Nominal', 'Gini Index', 'HDI', 'Covid Cases', 'Vaccines'])
        # print(results)
        for country in results:
            print_country(country)
        #self.poutput('App')

    def do_capitalInfo(self, Cname):
        """
        capitalInfo is used to get all the data about a specific capital
        Usage:
        capitalInfo <capital_name>        
        Arguments:
        - capital_name: the name of the capital to be searched
        """
        Cinfo_query = f"SELECT * FROM Capital C WHERE C.name LIKE '%{Cname}%'"
        cursor.execute(Cinfo_query)
        results = cursor.fetchall()
        if not results:
            print("Capital name does not exist!")
            return
        results = tabulate(results, headers=['Capital Name', 'Country Name', 'Population', 'Governer', 'Area', 'Coordinates'])
        print(results)
        # for x in results:
        #     print(x)
        #self.poutput('App')
    
    def do_presidentInfo(self, Pname):
        """
        presidentInfo is used to get all the data about a specific president/monarch
        Usage:
        presidentInfo <president_name>        
        Arguments:
        - president_name: the name of the president to be searched
        """
        Pinfo_query = f"SELECT * FROM President P WHERE P.name LIKE '%{Pname}%'"
        cursor.execute(Pinfo_query)
        results = cursor.fetchall()
        if not results:
            print("President name does not exist!")
            return
        results = tabulate(results, headers=['Country Name', 'President Name', 'Birthdate', 'Political Party', 'Assumed Office'])
        print(results)
        #self.poutput('App')
    
    def do_top10countries_global(self, args):
        """
        top10countries_global is used to show the top 10 countries by GDP, population, area, GDP per capita globally.
        Usage:
        top10countries_global <args>
        Arguments: 
        - args: the type of data to rank the countries by.
                It can take the following values:
                + gdp_pp: to rank by gross domestic product based on purchasing power parity
                + gdp_nominal: to rank by the normal GDP
                + population: to rank by population
                + area: to rank by area
        """
        try:
            top10global_query = f"SELECT C.name, C.{args} FROM Country C ORDER BY C.{args} DESC LIMIT 10"
            cursor.execute(top10global_query)
            results = cursor.fetchall()
            results = tabulate(results, headers=['Country Name', args])
            print(results)
        except Exception as e:
            print("Please enter value from [gdp_pp, gdp_nominal, population, or area] to rank the countries")
            print(e)
        #self.poutput('App')

    def do_top10countries_continent(self, args):
        """
        top10countries_continent is used to show the top 10 countries by GDP, population, area, GDP per capita within a continent.
        Usage:
        top10countries_continent <continent>,<args>
        Arguments: 
        - continent: the continent name to search within
        - args: the type of data to rank the countries by.
                It can take the following values:
                + gdp_pp: to rank by gross domestic product based on purchasing power parity
                + gdp_nominal: to rank by the normal GDP
                + population: to rank by population
                + area: to rank by area
        """
        continent = args.split(',')[0]
        col_name = args.split(',')[1]
        try:
            top10continent_query = f"SELECT C.name, C.{col_name}, C.continent FROM Country C WHERE C.continent LIKE '%{continent}%'\
                        ORDER BY C.{col_name} DESC LIMIT 10"
            cursor.execute(top10continent_query)
            results = cursor.fetchall()
            results = tabulate(results, headers=['Country Name', col_name, 'Continent'])
            print(results)
        except Exception as e:
            print("Please enter value from [gdp_pp, gdp_nominal, population, or area] to rank the countries")
            print (e)
        #self.poutput('App')

    def do_reviewsAbout(self, country):
        """
        reviewsAbout is used to view existing reviews on a given country
        Usage:
        reviewsAbout <country>
        Arguments
        - country: the name of the country to retrieve the reviews
        """
        review_query = f"SELECT username, travel_date, rating, txt_review FROM User_review WHERE country_name LIKE '%{country}%'"
        cursor.execute(review_query)
        results = cursor.fetchall()
        if not results:
            print(f"There are no reviews about {country}!")
            return
        results = tabulate(results, headers=['Username', 'Travel Date', 'Rating', 'Review'])
        print(results)
        #self.poutput('App')

    def do_covidCases(self, args):
        """
        covidCases is used to identify the top and bottom 5 countries in each continent in terms of covid cases
        To use covidCases, please enter the arguments in the follwing comma seperated format: 
        covidCases <continent>,<order>
        Arguments:
        - continent: the name of the continent to search within
        - order: Top to get the top 5 countries, or Bottom to get the Bottom 5 countries
        """
        if (len(args.split(',')) < 2):
            print("Please enter the arguments in the follwing form <Continent>,<Top/Bottom>")
            return

        continent = args.split(',')[0]
        order = args.split(',')[1].strip()

        if order in ['Top', 'top', 't', 'top5', 'Top5', 'desc', 'DESC']:
            order = 'DESC'
            print(f'Top 5  Countries in {continent} with COVID cases')
        else:
            order = 'ASC'
            print(f'Bottom 5  Countries in {continent} with COVID cases')
        
        covid_query = f"SELECT C.name, C.continent, C.covid_cases FROM Country C WHERE C.covid_cases IS NOT NULL\
                        AND C.continent LIKE '%{continent}%' ORDER BY C.covid_cases {order} LIMIT 5"
        cursor.execute(covid_query)
        results = cursor.fetchall()
        if not results:
            print(f"Please make sure that continent name is correct!")
            return
        results = tabulate(results, headers=['Country Name', 'Continent', 'Covid Cases'])
        print(results)
        #self.poutput('App')

    def do_vaccines(self, args):
        """
        vaccines is used to identify the top and bottom 5 countries in each continent in terms of vaccination rate
        To use vaccines, please enter the arguments in the follwing comma seperated format: 
        vaccines <continent>,<order>
        Arguments:
        - continent: the name of the continent to search within
        - order: Top to get the top 5 countries, or Bottom to get the Bottom 5 countries
        """
        if (len(args.split(',')) < 2):
            print("Please enter the arguments in the follwing form <Continent>,<Top/Bottom>")
            return

        continent = args.split(',')[0]
        order = args.split(',')[1].strip()

        if order in ['Top', 'top', 't', 'top5', 'Top5', 'desc', 'DESC']:
            order = 'DESC'
            print(f'Top 5  Vaccinated Countries in {continent}\n')
        else:
            order = 'ASC'
            print(f'Bottom 5 Vaccinated Countries in {continent} with COVID cases\n')
        
        vaccination_query = f"SELECT C.name, C.continent, C.vaccines FROM Country C WHERE C.vaccines IS NOT NULL\
                        AND C.continent LIKE '%{continent}%' ORDER BY C.vaccines {order} LIMIT 5"
        cursor.execute(vaccination_query)
        results = cursor.fetchall()
        if not results:
            print(f"Please make sure that continent name is correct!")
            return
        results = tabulate(results, headers=['Country Name', 'Continent', 'COVID Vaccines'])
        print(results)
        #self.poutput('App')
    
    cmd2.categorize((do_createUser,
                    do_addReview,
                    do_countriesWithLegislature,
                    do_countryOfCapital,
                    do_countryWithPhoneNo,
                    do_countryByDrivingside,
                    do_countryInfo,
                    do_capitalInfo,
                    do_presidentInfo,
                    do_top10countries_global,
                    do_top10countries_continent,
                    do_reviewsAbout,
                    do_covidCases,
                    do_vaccines), CMD_CAT_APP_MGMT)

def main():
    instant = wgs()
    instant.cmdloop()

if __name__ == "__main__":
    main()