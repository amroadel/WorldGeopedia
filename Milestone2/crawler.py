# %%
from pandas.core.frame import DataFrame
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
#%%
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



# %%
class Country:
    def __init__(self, name, continent, url):   
        '''
        A wrapper for a country page content
        '''
        self.url = url
        self.name = name
        self.capital = None
        self.capital_url = None
        self.president = None
        self.president_url = None
        self.calling_code = None
        self.driving_side = None
        self.gov_type = None
        self.continent = continent
        self.population = None
        self.area = None
        self.water_percentage = None
        self.gdp_pp = None
        self.gdp_nominal = None
        self.gini_index = None
        self.hdi = None
        self.covid_cases = None
        self.vaccines = None
        self.legislature = None
        self.timezone = []
        self.currency = []
        self.official_lang = []
    
    def parse_country_data(self):
        '''
        Parse the required information for each country
        '''
        rates = {'million':1_000_000, 'billion':1_000_000_000, 'trillion': 1_000_000_000_000}
        html_data = requests.get(self.url,'parser.html').text
        soupObj = BeautifulSoup(html_data,'html.parser')
        table_rows = (soupObj.find(class_ = "infobox ib-country vcard"))
        for ref in table_rows.find_all("sup", {'class':'reference'}): 
            ref.decompose()

        for img in table_rows.find_all("a", {'class':'image'}): 
            img.decompose()
        
        for style in table_rows.find_all("style", {}): 
            style.decompose()

        country_name = table_rows.find('div', {'class':'fn org country-name'})
        if country_name:
            country_name = country_name.text.strip(' ')

        calling_code = table_rows.select_one('th:-soup-contains("Calling code") + td')
        if calling_code:
            calling_code = calling_code.text.strip(' ')

        driving_side = table_rows.select_one('th:-soup-contains("Driving side") + td')
        if driving_side:
            driving_side = driving_side.text.strip(' ')[0]

        gov_type = table_rows.select_one('th:-soup-contains("Government") + td')
        if gov_type:
            gov_type = gov_type.text.strip(' ')

        p = table_rows.select_one('tr:-soup-contains("Population rank")')
        if p: p.decompose()

        d = table_rows.select_one('tr:-soup-contains("Density")')
        if d: d.decompose()

        r = table_rows.select_one('tr:-soup-contains("Rank")')
        if r: r.decompose()

        population = table_rows.select_one('th:-soup-contains("Population") + td')
        if not population:
            try:
                population = table_rows.select_one('th:-soup-contains("Population")')
                population = population.find_parent()
                population = population.find_next_sibling().select_one('td')
            except:
                population = None
        if population:
            population = population.text.strip(' ')
            population = re.sub(r'\([\w\s]+\)', "", population)
            population = population.replace(',', '')
            population = float(re.findall(r'\d+\.\d+|\d+',population)[0])
            

        area = table_rows.select_one('th:-soup-contains("Area") + td:-soup-contains("km")')
        if not area:
            try:
                area = table_rows.select_one('th:-soup-contains("Area")')
                area = area.find_parent()
                area = area.find_next_sibling().select_one('td:-soup-contains("km")')
            except:
                area = None
        if area:
            area = area.text.strip(' ')
            area = re.sub(r'\([\w\s]+\)', "", area)
            area = area.replace(',', '')
            area = area.replace('km2', '')
            area = area.replace('sq', '')
            area = area.replace('mi', '')
            area = float(re.findall(r'\d+\.\d+|\d+',area)[0])
   

        water_percentage = table_rows.select_one('th:-soup-contains("Water") + td')
        if water_percentage:
            water_percentage = list(water_percentage.children)
            for i in range(len(water_percentage)):
                if water_percentage[i].text != '':
                    water_percentage = water_percentage[i].text
                    if water_percentage.strip() in ['negligible', 'Negligible', 'n/a']:
                        water_percentage = 0.0
                    else:
                        water_percentage = float(re.findall(r'\d+\.\d+|\d+',(water_percentage.replace('%', '')))[0])
                    break

        try:
            gdp_pp = table_rows.select_one('th:-soup-contains("PPP")').find_parent()
            gdp_pp = gdp_pp.find_next_sibling().select_one('th:-soup-contains("Total") + td:-soup-contains("$")')
        except:
            gdp_pp = None

        if gdp_pp:
            gdp_pp = gdp_pp.text.replace(',','')
            gdp_pp = re.findall(r'\d+\.\d+\s+\w+|\d+\s+\w+', gdp_pp)[0].split()
            if gdp_pp[1] not in rates.keys():
                gdp_pp = float(gdp_pp[0])
            else:
                gdp_pp = float(gdp_pp[0]) * rates[gdp_pp[1]]

                
        try:
            gdp_nominal = table_rows.select_one('th:-soup-contains("nominal")').find_parent()
            gdp_nominal = gdp_nominal.find_next_sibling().select_one('th:-soup-contains("Total") + td:-soup-contains("$")')
        except:
            gdp_nominal = None

        if gdp_nominal:
            gdp_nominal = gdp_nominal.text.replace(',','')
            gdp_nominal = re.findall(r'\d+\.\d+\s+\w+|\d+\s+\w+', gdp_nominal)[0].split()
            if gdp_nominal[1] not in rates.keys():
                gdp_nominal = float(gdp_nominal[0])
            else:
                gdp_nominal = float(gdp_nominal[0]) * rates[gdp_nominal[1]]



        gini_index = table_rows.select_one('th:-soup-contains("Gini") + td')
        if gini_index:
            gini_index = list(gini_index.children)
            for i in range (len(gini_index)):
                if gini_index[i].text != '':
                    gini_index = gini_index[i].text.strip('( )')
                    gini_index = float(re.findall(r'\d+\.\d+|\d+', gini_index)[0])
                    break

        hdi = table_rows.select_one('th:-soup-contains("HDI") + td')
        if hdi:
            hdi = list(hdi.children)
            for i in range (len(hdi)):
                if hdi[i].text != '':
                    hdi = hdi[i].text.strip('( )')
                    hdi = float(re.findall(r'\d+\.\d+|\d+', hdi)[0])
                    break
        try:
            capital = table_rows.select_one('th:-soup-contains("Capital") + td')
            capital = capital.find('a', {})
            capital_url = capital.get('href')
            # capital = capital.text
            capital = capital.get('title')
        except:
            capital_url = f'/wiki/{self.name}'
            capital = self.name

        # Delete Kingdom to not conflict with King
        kingdom = table_rows.select_one('th:-soup-contains("Kingdom")')
        if kingdom: 
            kingdom.decompose()

        # Delete President of 
        president_of = table_rows.select_one('th:-soup-contains("President of")')
        if president_of: 
            president_of.decompose()
        president = table_rows.select_one('th:-soup-contains("President") + td') \
                    or table_rows.select_one('th:-soup-contains("Monarch") + td') \
                    or table_rows.select_one('th:-soup-contains("Head of State") + td') \
                    or table_rows.select_one('th:-soup-contains("King") + td') \
                    or table_rows.select_one('th:-soup-contains("Chairman") + td') \
                    or table_rows.select_one('th:-soup-contains("Prime Minister") + td') \
                    or table_rows.select_one('th:-soup-contains("Sultan") + td')\
                    or table_rows.select_one('th:-soup-contains("Captains Regent") + td')\
                    or table_rows.select_one('th:-soup-contains("Federal Council") + td')
                    
        if president:
            president = president.find('a', {})
            president_url = president.get('href')
            president_name = president.get('title')


        legislature = table_rows.select_one('th:-soup-contains("Legislature") + td')
        if legislature:
            legislature = list(legislature.children)
            for i in range(len(legislature)):
                if legislature[i].text != '':
                    legislature = legislature[i].text.strip('( )')
                    legislature = legislature.replace('\n', ' ')
                    break
        if not legislature or legislature == ' ':
            legislature = None

        #Parse Currency
        currency_ = table_rows.select_one('th:-soup-contains("Currency") + td')
        currency_ = currency_.find_all('li', {})
        if len(currency_) > 0:
            currency = []
            for i in range(len(currency_)):
                a_li = currency_[i].find('a', title=True)
                if a_li:
                    currency.append(a_li.text.strip(' '))
                else: 
                    currency.append(currency_[i].text.strip(' '))
                # break
        else:
            currency = []
            currency_ = table_rows.select_one('th:-soup-contains("Currency") + td')
            a_li = currency_.find('a', title=True)
            if a_li:
                currency.append(a_li.text.strip(' '))
            elif currency_:
                currency.append(currency_.text.strip(' '))

        # Parse languages
        languages_ = table_rows.select_one('th:-soup-contains("language") + td')
        languages_ = languages_.find_all('li', {})
        if len(languages_) > 0:
            official_lang = []
            for i in range(len(languages_)):
                a_li = languages_[i].find('a', title=True)
                if a_li:
                    official_lang.append(a_li.text.strip(' '))
                    # break
                # elif languages_: 
                #     official_lang.append(languages_.text.strip(' '))
        else:
            official_lang = []
            languages_ = table_rows.select_one('th:-soup-contains("language") + td')
            a_li = languages_.find('a', title=True)
            if a_li:
                official_lang.append(a_li.text.strip(' '))
            elif languages_: 
                official_lang.append(languages_.text.strip(' '))

        #Parse Timezone
        timezone = set()
        timezone_ = table_rows.select_one('th:-soup-contains("zone") + td')
        if timezone_:
            timezone_ = timezone_.text.split(',')
            for t in timezone_:
                # t = re.sub(r'\([\w\s]+\)', "", t)
                timezone.add(t)

        timezone_s = table_rows.select_one('th:-soup-contains("Summer") + td')
        if timezone_s:
            timezone_s = timezone_s.text.split(',')
            for ts in timezone_s:
                # ts = re.sub(r'\([\w\s]+\)', "", ts)
                timezone.add(ts)

        self.name = country_name
        self.capital = capital
        self.capital_url = capital_url
        self.president = president_name
        self.president_url = president_url
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
        self.legislature = legislature
        self.timezone = timezone
        self.currency = currency
        self.official_lang = official_lang

    def get_single_valued_attr(self):
        return {'name':self.name,
                'continent':self.continent,
                'capital':self.capital,
                'president':self.president,
                'calling_code':self.calling_code,
                'driving_side':self.driving_side,
                'gov_type':self.gov_type,
                'population':self.population,
                'area':self.area,
                'water_percentage':self.water_percentage,
                'gdp_pp':self.gdp_pp,
                'gdp_nominal':self.gdp_nominal,
                'gini_index':self.gini_index,
                'hdi':self.hdi,
                'legislature':self.legislature}

    # Getters
    def get_capital_name(self):
        return self.capital

    def get_capital_url(self):
        return self.capital_url

    def get_president_name(self):
        return self.president

    def get_president_url(self):
        return self.president_url

    # Getters for multi-valued attr
    def get_timezone(self):
        return self.timezone

    def get_currency(self):
        return self.currency

    def get_official_lang(self):
        return self.official_lang

class Capital:
    def __init__(self, name, url, country_name):
        self.name = name
        self.url = f'https://en.wikipedia.org{url}'
        self.country_name = country_name
        self.population = None
        self.governor = None
        self.area = None
        self.coordinates = None
    
    def parse_capital_data(self):

        if self.name in ['City-state', 'De jure', ' De_jure']:
            return

        # Read the table
        html_data = requests.get(self.url,'parser.html').text
        soupObj = BeautifulSoup(html_data,'html.parser')
        table_rows = (soupObj.find(class_ = "infobox"))
        for ref in table_rows.find_all("sup", {'class':'reference'}): 
            ref.decompose()

        p = table_rows.select_one('tr:-soup-contains("Population rank")')
        if p: p.decompose()

        d = table_rows.select_one('tr:-soup-contains("Density")')
        if d: d.decompose()

        r = table_rows.select_one('tr:-soup-contains("Rank")')
        if r: r.decompose()

        # Parse population
        population = table_rows.select_one('th:-soup-contains("Population") + td')
        if not population:
            try:
                population = table_rows.select_one('th:-soup-contains("Population")')
                population = population.find_parent()
                population = population.find_next_sibling().select_one('td')
            except:
                population = None
        if population:
            population = population.text.strip(' ')
            population = re.sub(r'\([\w\s]+\)', "", population)
            population = population.replace(',', '')
            population = float(re.findall(r'\d+\.\d+|\d+', population)[0])

        # Parse Area
        area = table_rows.select_one('th:-soup-contains("Area") + td:-soup-contains("km")')
        if not area:
            try:
                area = table_rows.select_one('th:-soup-contains("Area")')
                area = area.find_parent()
                area = area.find_next_sibling().select_one('td:-soup-contains("km")')
            except:
                area = None
        if area:
            area = area.text.strip(' ')
            area = re.sub(r'\([\w\s]+\)', "", area)
            area = area.replace(',', '')
            area = area.replace('km2', '')
            area = area.replace('sq', '')
            area = area.replace('mi', '')
            area = float(re.findall(r'\d+\.\d+|\d+', area)[0])
        
        #Parse Coordinates
        coordinates = table_rows.find('span', {'class':'geo-dec'})
        if coordinates:
            coordinates = coordinates.text

        # Delete Governorate to not conflict with Governor
        governorate = table_rows.select_one('th:-soup-contains("Governorate")')
        if governorate: 
            governorate.decompose()
        # Parse Governor/Mayor
        governor = table_rows.select_one('th:-soup-contains("Governor") + td') \
                   or table_rows.select_one('th:-soup-contains("Mayor") + td')
        
        if governor:
            governor = governor.text

        self.population = population
        self.governor = governor
        self.area = area
        self.coordinates = coordinates

    def get_parsed_attr(self):
        return {'name':self.name,
                'country_name':self.country_name,
                'population':self.population,
                'governor':self.governor,
                'area':self.area,
                'coordinates':self.coordinates}

class President: 
    def __init__(self, name, url, country_name):
        self.name = name
        self.url = f'https://en.wikipedia.org{url}'
        self.country_name = country_name
        self.birthdate = ''
        self.political_party = ''
        self.assumed_office = ''

    def parse_president_data(self):
        html_data = requests.get(self.url,'parser.html').text
        soupObj = BeautifulSoup(html_data,'html.parser')
        table_rows = (soupObj.find(class_ = "infobox vcard"))
        for ref in table_rows.find_all("sup", {'class':'reference'}): 
            ref.decompose()

        #Parse assumed office date
        assumed_office = table_rows.select_one('td:-soup-contains("Assumed office")') \
                     or table_rows.select_one('th:-soup-contains("Reign") + td')
        if assumed_office:
            remove = assumed_office.find('b', {})
            if remove: remove.decompose()
            assumed_office = assumed_office.text.replace(',', '')
            # print(assumed_office)
            assumed_office = re.findall(r'\d+\s+\w+\s+\d+|\w+\s+\d+\s+\d+',assumed_office)[0]
        
        #Parse birthdate
        birthdate = table_rows.find('span', {'class':'bday'})
        if birthdate:
            birthdate = birthdate.text.strip(' ')
        
        #Parse political party
        political_party = table_rows.select_one('th:-soup-contains("Political party") + td')
        if political_party:
            political_party = political_party.find('a', title = True)
            political_party = political_party.text.strip(' ')
        
        self.birthdate = birthdate
        self.political_party = political_party
        self.assumed_office = assumed_office

    def get_parsed_attr(self):
        return {'name':self.name,
                'country_name':self.country_name,
                'birthdate':self.birthdate,
                'political_party':self.political_party,
                'assumed_office':self.assumed_office}


def main():
    continents = ['Africa','North_America', 'Asia', 'South_America', 'Europe', 'Oceania']
    countries_info = get_countries(continents)
    
    countries = []
    capitals= []
    presidents = []
    official_languages = []
    currencies = []
    timezones = []
    for index, country in countries_info.iterrows():

        if country['Name'] == 'Vatican City':
            continue
        try:
            country_data = Country(country['Name'], country['Continent'], country['URL'])
            country_data.parse_country_data()
            countries.append(country_data.get_single_valued_attr())
            

            official_langs = country_data.get_official_lang()
            for lang in official_langs:
                official_languages.append({'country_name':country['Name'], 'official_language':lang})

            curr = country_data.get_currency()
            for c in curr:
                currencies.append({'country_name':country['Name'], 'currency':c})

            tzones = country_data.get_timezone()
            for zone in tzones:
                timezones.append({'country_name':country['Name'], 'timezone':zone})        

            capital_name = country_data.get_capital_name()
            capital_url = country_data.get_capital_url()
            capital_data = Capital(capital_name, capital_url, country['Name'])
            capital_data.parse_capital_data()
            capitals.append(capital_data.get_parsed_attr())

            president_name = country_data.get_president_name()
            president_url = country_data.get_president_url()
            president_data = President(president_name, president_url, country['Name'])
            president_data.parse_president_data()
            presidents.append(president_data.get_parsed_attr())
        except Exception as e:
            print('Problem with:', country['Name'], ' index:', index)
            print(e)

        # if index == 10:
        #     break


    countries_info.to_csv("countries_urls.csv", sep=',', encoding='utf-8', index=False)

    countries = pd.DataFrame.from_records(countries)
    countries = countries.drop(columns=['capital', 'president'])
    countries.to_csv("data/countries.csv", sep=',', encoding='utf-8-sig', index=False)

    capitals= pd.DataFrame.from_records(capitals)
    capitals.to_csv("data/capitals.csv", sep=',', encoding='utf-8-sig', index=False)

    presidents = pd.DataFrame.from_records(presidents)
    presidents.to_csv("data/presidents.csv", sep=',', encoding='utf-8-sig', index=False)

    official_languages = pd.DataFrame.from_records(official_languages)
    official_languages.to_csv("data/official_languages.csv", sep=',', encoding='utf-8-sig', index=False)

    currencies = pd.DataFrame.from_records(currencies)
    currencies.to_csv("data/currencies.csv", sep=',', encoding='utf-8-sig', index=False)

    timezones = pd.DataFrame.from_records(timezones)
    timezones.to_csv("data/timezones.csv", sep=',', encoding='utf-8-sig', index=False)



if __name__ == "__main__":
    main()

# country_data = Country('United States', 'North America', 'https://en.wikipedia.org/wiki/United_States')
# country_data.parse_country_data()
# x = country_data.get_single_valued_attr()
# capital_data = Capital('De jure', '/wiki/De_jure', 'Switzerland')
# capital_data.parse_capital_data()

# president = President('Moon_Jae-in','/wiki/Moon_Jae-in', 'South_Korea')
# president.parse_president_data()
# print(x)
# print(capital_data.get_parsed_attr())
# print(president.get_parsed_attr())