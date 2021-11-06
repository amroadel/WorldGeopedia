# %%
from pandas.core.frame import DataFrame
import requests
import pandas as pd
from bs4 import BeautifulSoup
#%%
def get_countries(continent):
    countries = pd.DataFrame(columns=['Country', 'URL'])
    url = f"https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_in_{continent}"
    html_data = requests.get(url,'parser.html').text
    soupObj = BeautifulSoup(html_data,'html.parser')
    countries_table = (soupObj.find_all('table', {'class':'wikitable sortable'})[0])
    body = countries_table.find('tbody', {})
    tr = body.find_all('tr', {})

    for i in range(1, len(tr)):
        td = tr[i].find_all('td', {})
        # Note: Oceania has index 3
        # Note: North America has index 1 others are 2
        a = td[2].find('a', {})
        country_name = a.get("title")
        country_url = a.get("href")
        countries = countries.append({'Country':country_name, 'URL':f'https://en.wikipedia.org{country_url}'}, ignore_index = True)
    return countries

#%%
c =get_countries('South_America')
c.to_csv("North_America_countries.csv", sep=',', encoding='utf-8', index=False)

# %%
class Country:
    def __init__(self, name, continent, url):   
        '''
        A wrapper for a country page content
        '''
        self.url = url
        self.name = name
        self.calling_code = ''
        self.driving_side = ''
        self.gov_type = ''
        self.continent = continent
        self.population = -1
        self.area = -1
        self.water_percentage = -1
        self.gdp_pp = -1
        self.gdp_nominal = -1
        self.gini_index = -1
        self.hdi = -1
        self.covid_cases = -1
        self.vaccines = -1
        self.timezone = []
        self.currency = []
        self.legislature = []
        self.official_lang = []
    
    def parse_country_data(self):
        '''
        Parse the required information for each country
        '''
        html_data = requests.get(self.url,'parser.html').text
        soupObj = BeautifulSoup(html_data,'html.parser')
        table_rows = (soupObj.find(class_ = "infobox ib-country vcard"))
        country_name = table_rows.find('div', {'class':'fn org country-name'}).text
        calling_code = table_rows.select_one('th:-soup-contains("Calling code") + td').text
        driving_side = table_rows.select_one('th:-soup-contains("Driving side") + td').text
        gov_type = table_rows.select_one('th:-soup-contains("Government") + td').text




