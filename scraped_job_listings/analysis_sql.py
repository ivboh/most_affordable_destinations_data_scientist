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

cur.execute("SELECT job_location,salary FROM indeed WHERE salary LIKE '% a year';")
for item in cur.fetchall():
    print (item[0],average_salary(item[1]))

