import pandas as pd
from sqlalchemy import create_engine
import pymysql
from faker import Faker 
from random import randrange

def fake_user_and_review():
    Faker.seed(0)
    faker = Faker()
    users = []
    reviews = []
    for i in range (5):
        fake_profile = (faker.profile())
        travel_date = faker.date_time()
        rating = randrange(1,10)
        review = faker.text()
        country = 'Egypt'

        fake_user = {'username':fake_profile['username'], 'email':fake_profile['mail'],\
            'gender':fake_profile['sex'], 'birthdate':fake_profile['birthdate']}

        fake_review = {'id':i,'travel_date':travel_date,'rating':rating, 'txt_review':review, \
            'username':fake_profile['username'],'country_name':country}
        
        users.append(fake_user)
        reviews.append(fake_review)

    users = pd.DataFrame.from_records(users)
    reviews = pd.DataFrame.from_records(reviews)
           
    return users, reviews

def inser_records_into_db(countries, capitals, presidents, currencies, official_languages, timezones):
    hostname="127.0.0.1"
    dbname="WGS"
    uname="vscode"
    pwd="password"

    try: 
        connection = pymysql.connect(host= hostname, user= uname, passwd= pwd, db= dbname)
        cursor=connection.cursor()

        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                    .format(host=hostname, db=dbname, user=uname, pw=pwd))
    except Exception as e:
        print(e) 

    # Read CSV files into dataframes
    # capitals = pd.read_csv('data/capitals.csv') 
    # currencies = pd.read_csv('data/currencies.csv')
    # official_languages = pd.read_csv('data/official_languages.csv')
    # presidents = pd.read_csv('data/presidents.csv')
    # timezones = pd.read_csv('data/timezones.csv')
    # countries = pd.read_csv('data/countries.csv')

    # countries['name'] = capitals['country_name']
    
    # Truncate tables to avoid adding duplicate data
    truncate = True
    if truncate:

        truncate_capital = "TRUNCATE TABLE `Capital`"
        cursor.execute(truncate_capital)

        truncate_president = "TRUNCATE TABLE `President`"
        cursor.execute(truncate_president)

        truncate_currency = "TRUNCATE TABLE `currency`"
        cursor.execute(truncate_currency)

        truncate_official_lang = "TRUNCATE TABLE `official_lang`"
        cursor.execute(truncate_official_lang)

        truncate_timezone = "TRUNCATE TABLE `timezone`"
        cursor.execute(truncate_timezone)
        
        truncate_review = "TRUNCATE TABLE `User_review`"
        cursor.execute(truncate_review)
        
        # These setters are important to be able to truncate the country table
        setter1 = 'SET FOREIGN_KEY_CHECKS = 0'
        cursor.execute(setter1)
        
        truncate_country = "TRUNCATE TABLE `Country`"
        cursor.execute(truncate_country)

        truncate_user = "TRUNCATE TABLE `User`"
        cursor.execute(truncate_user)

        setter2 = 'SET FOREIGN_KEY_CHECKS = 1'
        cursor.execute(setter2)

    users, reviews = fake_user_and_review()
    countries.to_sql(name='Country', con= engine, if_exists= 'append', index= False )
    capitals.to_sql(name='Capital', con= engine, if_exists= 'append', index= False )
    currencies.to_sql(name='currency', con= engine, if_exists= 'append', index= False )
    official_languages.to_sql(name='official_lang', con= engine, if_exists= 'append', index= False )
    timezones.to_sql(name='timezone', con= engine, if_exists= 'append', index= False )
    presidents.to_sql(name='President', con= engine, if_exists= 'append', index= False )
    users.to_sql(name='User', con= engine, if_exists= 'append', index= False )
    try:
        reviews.to_sql(name='User_review', con= engine, if_exists= 'append', index= False )
    except:
        print('Problem with storing fake reviews, bs fakes')

    users.to_csv("data/users.csv", sep=',', encoding='utf-8', index=False)
    reviews.to_csv("data/reviews.csv", sep=',', encoding='utf-8', index=False)
