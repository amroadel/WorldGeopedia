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
        self.capital = ''
        self.capital_url = ''
        self.president = ''
        self.president_url = ''
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

        country_name = table_rows.find('div', {'class':'fn org country-name'})
        if country_name is not None:
            country_name = country_name.text

        calling_code = table_rows.select_one('th:-soup-contains("Calling code") + td')
        if calling_code is not None:
            calling_code = calling_code.text

        driving_side = table_rows.select_one('th:-soup-contains("Driving side") + td')
        if driving_side is not None:
            driving_side = driving_side.text

        gov_type = table_rows.select_one('th:-soup-contains("Government") + td')
        if gov_type is not None:
            gov_type = gov_type.text

        population = table_rows.select_one('th:-soup-contains("Population")').find_parent()
        population = population.find_next_sibling().select_one('td')
        if population is not None:
            population = list(population.children)
            for i in range(len(population)):
                if population[i].text != '':
                    population = population[i].text
                    break

        area = table_rows.select_one('th:-soup-contains("Area")').find_parent()
        area = area.find_next_sibling().select_one('th:-soup-contains("Total") + td')
        if area is not None:
            area = list(area.children)
            for i in range (len(area)):
                if area[i].text != '':
                    area = area[i].text
                    break

        water_percentage = table_rows.select_one('th:-soup-contains("Water") + td')
        if water_percentage is not None:
            water_percentage = list(water_percentage.children)
            for i in range(len(water_percentage)):
                if water_percentage[i].text != '':
                    water_percentage = water_percentage[i].text
                    break

        gdp_pp = table_rows.select_one('th:-soup-contains("PPP")').find_parent()
        gdp_pp = gdp_pp.find_next_sibling().select_one('th:-soup-contains("Total") + td:-soup-contains("$")')
        if gdp_pp is not None:
            gdp_pp = list(gdp_pp.children)
            for i in range (len(gdp_pp)):
                if (gdp_pp[i].text.find("$") >= 0):
                    gdp_pp = gdp_pp[i].text
                    break

        gdp_nominal = table_rows.select_one('th:-soup-contains("nominal")').find_parent()
        gdp_nominal = gdp_nominal.find_next_sibling().select_one('th:-soup-contains("Total") + td:-soup-contains("$")')
        if gdp_nominal is not None:
            gdp_nominal = list(gdp_nominal.children)
            for i in range (len(gdp_nominal)):
                if (gdp_nominal[i].text.find("$") >= 0):
                    gdp_nominal = gdp_nominal[i].text
                    break

        gini_index = table_rows.select_one('th:-soup-contains("Gini") + td')
        if gini_index is not None:
            gini_index = list(gini_index.children)
            for i in range (len(gini_index)):
                if gini_index[i].text != '':
                    gini_index = gini_index[i].text
                    break

        hdi = table_rows.select_one('th:-soup-contains("HDI") + td')
        if hdi is not None:
            hdi = list(hdi.children)
            for i in range (len(hdi)):
                if hdi[i].text != '':
                    hdi = hdi[i].text
                    break

        capital = table_rows.select_one('th:-soup-contains("Capital") + td')
        capital = capital.find('a', {})
        capital_url = capital.get('href')
        capital = capital.get('title')

        self.name = country_name
        self.capital = capital
        self.capital_url = capital_url
        self.calling_code = calling_code
        self.driving_side = driving_side
        self.gov_type = gov_type
        self.population = population
        self.area = area
        self.water_percentage = water_percentage
        self.gdp_pp = gdp_pp
        self.gdp_nominal = gdp_nominal
        self.gini_index = gini_index
        self.hdi = hdi

        # self.covid_cases = -1
        # self.vaccines = -1
        # self.timezone = []
        # self.currency = []
        # self.legislature = []
        # self.official_lang = []


