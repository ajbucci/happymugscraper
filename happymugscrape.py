import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://happymugcoffee.com/collections/green-coffee"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find("table", class_="green-coffee")
coffees = results.find_all("a")
df = pd.DataFrame(columns = ['Coffee', 'Arrival', 'Link'])

baseURL = "https://happymugcoffee.com"
for coffee in coffees:
    coffee_page = requests.get(baseURL + coffee.get('href'))
    coffee_soup = BeautifulSoup(coffee_page.content, "html.parser")
    for elem in coffee_soup('p',text=re.compile(r'Arrival')):
        print(coffee.get_text() + ' ' + elem.get_text())
        row = pd.DataFrame([{'Coffee' : coffee.get_text(), 'Arrival' : elem.get_text(), 'Link' : baseURL + coffee.get('href')}])
        df = pd.concat([df,row], ignore_index = True)

pattern = re.compile(r"(\w\s\w)$")
arrival = df['Arrival'].str.extract(r'(\w*)\s*(\w*)$')

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

arrival[0] = arrival.apply(lambda row : month_string_to_number(row[0]), axis = 1)
arrival = arrival.rename(columns={0: "Month", 1: "Year"})
final = pd.concat([df, arrival], axis = 1)
final = final.drop(['Arrival'], axis = 1)
pd.set_option('display.max_colwidth', None)
final.sort_values(by=['Year', 'Month'], ascending = False)