import urllib.request
from bs4 import BeautifulSoup
import time
import numpy as np
import io
import re
import psycopg2 as pg2

    
def save_counts_salary_by_city2(city, state):
    '''
    The function
    1)generates a URL given a city and a state.
    2)get the webpage of data science job positions at the city/state from indeed.com
    3)parse the meta data of job listings under refine search 
    4)return a dictionary with key as different refine
        search category and values as a list of tuples, each element is a pair of
        specific search category value and the job counts
     
    Input: a pair of city and state
        e.g.  save_counts_salary_by_city2("Austin", "Texas")
    Return: a dictionary 
         {"by_salary": [("$70,000+", 3754),
                         ("$90,000+", 2736),
                         ("$115,000+", 1234)],
            "by_jobtyple":[("full time", 4321),
                            ("contract", 2222),
                            ("intern", 111)]
            "by_company":[("facebook", 778),
                            ("google", 432),
                            ("Micosfot", 123)]
         }   
    '''

    time.sleep(np.random.randint(30,50))
    URL = 'https://www.indeed.com/jobs?q=(%22data+science%22+or+%22data+scientist%22)&l={},+{}&radius=5'.format(city,state)
    print(URL)
    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')

    #parse meta data under for salary ranges    
    e = soup.findAll('div', {'id':'SALARY_rbo'}) #find('div', {'id':'refineresults'})
    temps=BeautifulSoup(str(e), 'html.parser')
    s = temps.findAll('span', {'class':'rbLabel'})
    c = temps.findAll('span', {'class':'rbCount'})
    s_list, c_list=[],[]
    for ss in s:
        salary= re.sub("[^0-9]", "", ss.get_text())
        salary= int(salary)
        s_list.append(salary)
    for cc in c:
        count = re.sub("[^0-9]", "", cc.get_text())
        count = int(count)
        c_list.append(count)
    refine_by_salary=zip(s_list, c_list)

    #parse meta data for different job types
    e = soup.findAll('div', {'id':'rb_Job Type'}) #find('div', {'id':'refineresults'})
    temps=BeautifulSoup(str(e), 'html.parser')
    s = temps.findAll('span', {'class':'rbLabel'})
    c = temps.findAll('span', {'class':'rbCount'})
    s_list, c_list=[],[]
    for ss in s:
        s_list.append(ss.get_text())
    for cc in c:
        count = re.sub("[^0-9]", "", cc.get_text())
        count = int(count)
        c_list.append(count)
    refine_by_jobtype=zip(s_list, c_list)

    #parse meta data for different company
    e = soup.findAll('div', {'id':'rb_Company'}) 
    temps=BeautifulSoup(str(e), 'html.parser')
    s = temps.findAll('span', {'class':'rbLabel'})
    c = temps.findAll('span', {'class':'rbCount'})
    s_list, c_list=[],[]
    for ss in s:
        s_list.append(ss.get_text())
    for cc in c:
        count = re.sub("[^0-9]", "", cc.get_text())
        count = int(count)
        c_list.append(count)
    refine_by_company=zip(s_list, c_list)

    #return parsed data
    return {'by_salary': refine_by_salary, 
            'by_jobtype':refine_by_jobtype,
            'by_company': refine_by_company}



conn = pg2.connect(dbname='dsjob', host='localhost',
                    password='docker', user='postgres')
conn.autocommit = True
cur = conn.cursor()


#cur.execute('DROP TABLE IF EXISTS refine_result2;')
query='''CREATE TABLE IF NOT EXISTS refine_result2 (
            city varchar(50) NOT NUll,
            state varchar(2) NOT NULL,
            by_category varchar(50) NOT NULL,
            category varchar(100) NOT NULL,
            counts int NOT NULL,
            PRIMARY KEY (city, state, by_category, category)
        );'''
cur.execute(query)
conn.commit()

major_cities= [('New York','NY') , ('San Francisco','CA'), ('Seattle','WA'), 
    ('Chicago','IL'), ('Boston', 'MA'), ('Washington','DC'), ('Austin', 'TX'), 
    ('Atlanta','GA'), ('Los Angeles', 'CA'), ('Arlington', 'VA'), ('Dallas', 'TX'), ('Cambridge', 'MA'),
    ('Houston', 'TX'), ('Mc Lean', 'VA'), ('Redwood City', 'CA'), ('Mountain View', 'CA')]

#in case the scrips runs for multiple times
#it's helpful only scraped cities not in the database
cur.execute("SELECT DISTINCT(city) FROM refine_result2;")
scrapped_cities = [item[0] for item in cur]


for e in major_cities:
    city, state = e
    city_search= "+".join(city.split(" "))
    if not city in scrapped_cities: 
        print(city+ " not scrapped")
        d=save_counts_salary_by_city2(city_search, state)
        for by_category in d:
            print (by_category)
            for v in d[by_category]:
                print(v)
                category, count = v
                cur.execute("INSERT INTO refine_result2(city, state, by_category, category, counts) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", [city, state, by_category, category, count])
                conn.commit()
cur.close()
conn.close()