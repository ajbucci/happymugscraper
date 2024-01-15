import os
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

csv_file_name = 'happy_mug_list.csv'
URL = "https://happymugcoffee.com/collections/green-coffee"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find("table", class_="green-coffee")
coffees = results.find_all("a")

updated_df = pd.DataFrame(columns = ['Coffee', 'Link', 'Month', 'Year'])
old_df = updated_df
if os.path.exists(csv_file_name):
    old_df = pd.read_csv(csv_file_name)

baseURL = "https://happymugcoffee.com"

def month_string_to_number(string):
    m = {
        'jan':1,
        'feb':2,
        'mar':3,
        'apr':4,
        'may':5,
        'jun':6,
        'jul':7,
        'aug':8,
        'sep':9,
        'oct':10,
        'nov':11,
        'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

def find_arrival(soup):
    arrival_pattern = re.compile(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{4})\b')
    for elem in soup('p'):
        arrival_search = re.search(arrival_pattern, elem.get_text())
        if arrival_search:
            if arrival_search.group(1):
                month = month_string_to_number(arrival_search.group(1))
                year = arrival_search.group(2)
            else:
                month = month_string_to_number(arrival_search.group(3))
                year = arrival_search.group(4)
            return (month, year)
    return (0, 0)

for coffee in coffees:
    link = baseURL + coffee.get('href')
    link_loc = old_df['Link']==link
    if any(link_loc):
        updated_df = pd.concat([updated_df, old_df[link_loc]], ignore_index = True)
    else:
        print('Scraping ' + coffee.get_text())
        coffee_page = requests.get(link)
        coffee_soup = BeautifulSoup(coffee_page.content, "html.parser")
        month, year = find_arrival(coffee_soup)
        row = pd.DataFrame([{'Coffee' : coffee.get_text(), 'Link' : link, 'Month' : month, 'Year' : year}])
        updated_df = pd.concat([updated_df,row], ignore_index = True)        

pd.set_option('display.max_colwidth', None)
updated_df['Year'] = pd.to_numeric(updated_df['Year'])
updated_df['Month'] = pd.to_numeric(updated_df['Month'])
updated_df = updated_df.sort_values(by=['Year', 'Month'], ascending = False, ignore_index=True)
print(updated_df)
updated_df.to_csv(csv_file_name, index=False)
# updated_df.sort_values(by=['Coffee'])