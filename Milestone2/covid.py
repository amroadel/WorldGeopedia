from pandas.core.frame import DataFrame
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

def get_countries(continents):
    index = {'North_America': 1,'Asia': 2, 'Africa': 2, 'South_America': 2, 'Europe': 2, 'Oceania': 3}
    countries = pd.DataFrame(columns=['Name', 'Continent', 'URL'])
    for continent in continents:
        url = f"https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_in_{continent}"
        html_data = requests.get(url,'parser.html').text
        soupObj = BeautifulSoup(html_data,'html.parser')
        countries_table = (soupObj.find_all('table', {'class':'wikitable sortable'})[0])
        body = countries_table.find('tbody', {})
        tr = body.find_all('tr', {})

        for i in range(1, len(tr)):
            td = tr[i].find_all('td', {})
            a = td[index[continent]].find('a', {})
            country_name = a.get("title")
            country_url = a.get("href")
            countries = countries.append({'Name':country_name, 'Continent':continent, 'URL':f'https://en.wikipedia.org{country_url}'}, ignore_index = True)
    
    countries = countries.drop_duplicates(subset=['Name'], keep='first')
    return countries

def make_url(country_name):
    country_url = re.sub(r'\(\w+\)|\(\w+\s\)', '', country_name)
    country_url = country_url.strip()
    country_url = country_url.replace(' ', '_')
    country_url = f'https://en.wikipedia.org/wiki/{country_url}'
    return country_url

def parse_covid_data(info_typ):
    url = {'covid_cases': 'https://news.google.com/covid19/map?hl=en-US&gl=US&ceid=US%3Aen',\
           'vaccines':'https://news.google.com/covid19/map?hl=en-US&gl=US&ceid=US%3Aen&state=4'}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')

    browser = webdriver.Chrome(options=chrome_options, executable_path='./chromedriver')
    browser.get(url[info_typ])

    element = browser.find_element_by_css_selector('tbody.ppcUXd')
    actions = ActionChains(browser)
    actions.move_to_element(element)
    actions.perform()

    html = browser.page_source
    soupObj = BeautifulSoup(html,'html.parser')
    table = (soupObj.find(class_ = "ppcUXd"))

    data = []
    for tr in list(table.children):
        country_name = tr.find("div", {'class':'pcAJd'}).text
        if country_name == 'Worldwide':
            continue
        
        info = tr.find_all("td", {'class':'l3HOY'})[0].text
        info = info.replace(',', '')
        try:
            info = float(info)
            data.append({'country_name': country_name, info_typ: info})
        except:
            data.append({'country_name': country_name, info_typ: None})

    data = pd.DataFrame.from_records(data)
    return data

def get_countries_and_covid():

    continents = ['Africa','North_America', 'Asia', 'South_America', 'Europe', 'Oceania']
    countries_info = get_countries(continents)

    covid_cases = parse_covid_data('covid_cases')
    covid_vaccines = parse_covid_data('vaccines')
    
    covid = pd.merge(covid_cases, covid_vaccines, on='country_name')
    covid['URL'] = covid['country_name'].apply(make_url)
    country_covid = pd.merge(countries_info, covid, on='URL', how= 'left')
    country_covid = country_covid.drop(columns=['country_name'])
    # country_covid.to_csv("data/country_covid.csv", sep=',', encoding='utf-8-sig', index=False)
    return country_covid

