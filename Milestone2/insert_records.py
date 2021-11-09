#%%
import pandas as pd
from sqlalchemy import create_engine
import pymysql

# %%
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
#%%
# Read CSV files into dataframes
capitals = pd.read_csv('data/capitals.csv', ',') 
currencies = pd.read_csv('data/currencies.csv', ',')
official_languages = pd.read_csv('data/official_languages.csv', ',')
presidents = pd.read_csv('data/presidents.csv', ',')
timezones = pd.read_csv('data/timezones.csv', ',')
countries = pd.read_csv('data/countries.csv', ',')
countries['covid_cases'] = 0
countries['vaccines'] = 0

# countries['name'] = capitals['country_name']
#%%
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
    
    # These setters are important to be able to truncate the country table
    setter1 = 'SET FOREIGN_KEY_CHECKS = 0'
    cursor.execute(setter1)
    
    truncate_country = "TRUNCATE TABLE `Country`"
    cursor.execute(truncate_country)

    setter2 = 'SET FOREIGN_KEY_CHECKS = 1'
    cursor.execute(setter2)

#%%
countries.to_sql(name='Country', con= engine, if_exists= 'append', index= False )
capitals.to_sql(name='Capital', con= engine, if_exists= 'append', index= False )
currencies.to_sql(name='currency', con= engine, if_exists= 'append', index= False )
official_languages.to_sql(name='official_lang', con= engine, if_exists= 'append', index= False )
timezones.to_sql(name='timezone', con= engine, if_exists= 'append', index= False )
presidents.to_sql(name='President', con= engine, if_exists= 'append', index= False )
