import pandas as pd

from crawler import Country
from crawler import Capital
from crawler import President
from covid import get_countries_and_covid
from insert_records import inser_records_into_db


def main():
    countries_info = get_countries_and_covid()
    
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
            country_data = Country(country['Name'], country['Continent'], country['URL'], country['covid_cases'], country['vaccines'])
            country_data.parse_country_data()
            countries.append(country_data.get_single_valued_attr())
            country_name = country_data.get_name()
            

            official_langs = country_data.get_official_lang()
            for lang in official_langs:
                official_languages.append({'country_name':country_name, 'official_language':lang})

            curr = country_data.get_currency()
            for c in curr:
                currencies.append({'country_name':country_name, 'currency':c})

            tzones = country_data.get_timezone()
            for zone in tzones:
                timezones.append({'country_name':country_name, 'timezone':zone})        

            capital_name = country_data.get_capital_name()
            capital_url = country_data.get_capital_url()
            capital_data = Capital(capital_name, capital_url, country_name)
            capital_data.parse_capital_data()
            capitals.append(capital_data.get_parsed_attr())

            president_name = country_data.get_president_name()
            president_url = country_data.get_president_url()
            president_data = President(president_name, president_url, country_name)
            president_data.parse_president_data()
            presidents.append(president_data.get_parsed_attr())
        except Exception as e:
            print('Problem with:', country_name, ' index:', index)
            print(e)

        # if index == 2:
        #     break


    

    countries = pd.DataFrame.from_records(countries)
    countries = countries.drop(columns=['capital', 'president'])

    capitals= pd.DataFrame.from_records(capitals)
    presidents = pd.DataFrame.from_records(presidents)
    official_languages = pd.DataFrame.from_records(official_languages)
    currencies = pd.DataFrame.from_records(currencies)
    timezones = pd.DataFrame.from_records(timezones)

    inser_records_into_db(countries, capitals, presidents, currencies, official_languages, timezones)
    
    countries_info.to_csv("countries_urls.csv", sep=',', encoding='utf-8', index=False)
    countries.to_csv("data/countries.csv", sep=',', encoding='utf-8-sig', index=False)
    capitals.to_csv("data/capitals.csv", sep=',', encoding='utf-8-sig', index=False)
    presidents.to_csv("data/presidents.csv", sep=',', encoding='utf-8-sig', index=False)
    official_languages.to_csv("data/official_languages.csv", sep=',', encoding='utf-8-sig', index=False)
    currencies.to_csv("data/currencies.csv", sep=',', encoding='utf-8-sig', index=False)
    timezones.to_csv("data/timezones.csv", sep=',', encoding='utf-8-sig', index=False)



if __name__ == "__main__":
    main()
