import urllib.request
from bs4 import BeautifulSoup
import time
import numpy as np
import io


def scrape_living_cost_page(city, state):
    '''
    The function takes a city and state as input:
    1) generate a URL
    2) get the web page from areavibes.com
    3) parse the web page
    4) returns the cost of living index as an integer,
        100 as national average.
        109 means the cost if higher at 109% of national average

    Input: city as a string, state as a string:
            e.g.  scrape_living_cost_page("Austin", "TX")
    Output: cost of living as an integer 
            e.g.  print(scrape_living_cost_page("Austin", "TX"))
                    109
    '''
    time.sleep(np.random.randint(30,50))
    URL= "https://www.areavibes.com/{}-{}/livability/".format(city,state)
    print(URL)
    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')
    a = soup.find('div', {'class':'facts-box-container'})
    soup = BeautifulSoup(str(a), 'html.parser')
    a = soup.find('div', {'class':'facts-box-body'})
    soup = BeautifulSoup(str(a), 'html.parser')
    a = soup.find('em')
    return(int(a.get_text()))


import psycopg2 as pg2
conn = pg2.connect(dbname='dsjob', host='localhost',
                    password='docker', user='postgres')
conn.autocommit = True
cur = conn.cursor()

#cur.execute('DROP TABLE IF EXISTS living_cost;')

query='''CREATE TABLE IF NOT EXISTS living_cost (
            city varchar(50) NOT NULL,
            state varchar(2) NOT NULL,
            cost int NOT NULL,
            PRIMARY KEY (city, state)
        );'''
cur.execute(query)
conn.commit()

major_cities= [('New York','NY') , ('San Francisco','CA'), ('Seattle','WA'), 
    ('Chicago','IL'), ('Boston', 'MA'), ('Washington','DC'), ('Austin', 'TX'), 
    ('Atlanta','GA'), ('Los Angeles', 'CA'), ('Arlington', 'VA'), ('Dallas', 'TX'), ('Cambridge', 'MA'),
    ('Houston', 'TX'), ('Mc Lean', 'VA'), ('Redwood City', 'CA'), ('Mountain View', 'CA')]

for e in major_cities:
    city, state = e
    if city== 'Mc Lean':
        city_search = 'mclean'
    else:
        city_search= "+".join(city.lower().split(" "))
    state_search = state.lower()
    living_cost = scrape_living_cost_page(city_search, state_search)
    
    cur.execute("INSERT INTO living_cost (city, state, cost) VALUES (%s,  %s, %s)", [city, state,living_cost])
    conn.commit()

cur.close()
conn.commit()
