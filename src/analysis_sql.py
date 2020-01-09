from bs4 import BeautifulSoup
import os
import re
import psycopg2 as pg2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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
    list_sort = [(l1[i],l2[i]) for i in range(len(l1))]
    list_sort.sort(key=lambda tup:tup[0])
    l1 = [s for s,c in list_sort]
    l2 = [c for s,c in list_sort]
    l2_shift =  l2[1:]
    l2_shift.append(0)
    l2 = [ a-b for a,b in zip(l2, l2_shift)]
    salary_avg = int(sum(s*c for (s,c) in zip(l1,l2))/sum(c for (s,c)  in zip(l1,l2)))
    d[(city, state)]=salary_avg    


cur.execute("SELECT * FROM living_cost")
for item in cur.fetchall():
    city, state, score = item
    salary_avg = d[(city, state)]
    d[(city, state)] = (salary_avg, int(salary_avg*100/score)) 

for e in d:
    print (e, d[e])

d_list = [(k, d[k][0], d[k][1]) for k in d]
city_list = [e[0] for e,_,_ in d_list]
salary_list = [e for _,e,_ in d_list]
disc_salary_list = [e for _,_,e in d_list]
print(city_list)
print(salary_list)
print(disc_salary_list)

ind = np.arange(len(city_list))
width=0.35
fig = plt.figure()
ax = fig.add_subplot()
s1 = ax.bar(ind, salary_list, width, color = 'blue')
s2 = ax.bar(ind+width, disc_salary_list, width, color = 'r')

ax.set_ylabel('Salary')
ax.set_title('Salary (adjusted) by city')
ax.set_xticks(ind)
ax.set_xticklabels(city_list)
ax.tick_params(axis = 'x', rotation =45)
ax.legend((s1,s2) ,  ('Salary', 'Salary adjusted by living cost'))
plt.show()

plt.show()
