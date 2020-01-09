from bs4 import BeautifulSoup
import os
import re
import psycopg2 as pg2
import numpy as np


def average_salary(salary_range_string):
    mean = np.mean([int(e.strip().replace("$","").replace("," , "")) for e in salary_range_string.replace("a year", "").replace("From", "").replace("Up to","").split("-")])
    return mean
    
conn = pg2.connect(dbname='dsjob', host='localhost',
                    password='docker', user='postgres')
conn.autocommit = True
cur = conn.cursor()
#cur.execute('DROP DATABASE IF EXISTS dsjob;')
#cur.execute('CREATE DATABASE dsjob;')

#cur.execute("SELECT job_location,salary FROM indeed WHERE job_location LIKE '%Austin, TX%' AND salary LIKE '% a year';")
cur.execute("SELECT job_location,salary FROM indeed WHERE salary LIKE '% a year';")

major_cities= [('New York','NY') , ('San Francisco','CA'), ('Seattle','WA'), 
    ('Chicago','IL'), ('Boston', 'MA'), ('Washington','DC'), ('Austin', 'TX'), 
    ('Atlanta','GA'), ('Los Angeles', 'CA'), ('Arlington', 'VA'), ('Dallas', 'TX'), ('Cambridge', 'MA'),
    ('Houston', 'TX'), ('Mc Lean', 'VA')]

'''
for e in major_cities:
    city,state =e
    cur.execute("SELECT job_location,salary FROM indeed WHERE salary LIKE job_location LIKE '%s, %s%';",['% a year',city, state])
    l = []
    for item in cur.fetchall():
        l.append(average_salary(item[1]))
    print(city, state, np.mean(l))
'''

d ={}
for e in major_cities:
    city, state = e
    cur.execute("SELECT * FROM refine_result WHERE by_category = 'by_salary' and city = %s and state = %s", [city,state])
    l1, l2 = [],[]
    for item in cur.fetchall():
        l1.append(int(item[3]))
        l2.append(int(item[4]))
    salary_avg = int(sum(s*c for (s,c) in zip(l1,l2))/sum(c for (s,c)  in zip(l1,l2)))
    d[(city, state)]=salary_avg    


cur.execute("SELECT * FROM living_cost")
for item in cur.fetchall():
    city, state, score = item
    salary_avg = d[(city, state)]
    d[(city, state)] = (salary_avg, int(salary_avg*100/score)) 

for e in d:
    print (e, d[e])

