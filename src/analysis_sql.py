from bs4 import BeautifulSoup
import os
import re
import psycopg2 as pg2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import ttest_ind, ttest_ind_from_stats, probplot
import pylab
import statsmodels.stats.api as sms

def average_salary(salary_range_string):
    mean = np.mean([int(e.strip().replace("$","").replace("," , "")) for e in salary_range_string.replace("a year", "").replace("From", "").replace("Up to","").split("-")])
    return mean

def hr_rate_to_salary(hour_rate_string):
    if not 'hour' in hour_rate_string:
        return None
    else:
        hour_rate = re.sub("[^0-9]" ,"",hour_rate_string)
        return (int(hour_rate)*52*40)

conn = pg2.connect(dbname='dsjob', host='localhost',
                    password='docker', user='postgres')
conn.autocommit = True
cur = conn.cursor()
#cur.execute('DROP DATABASE IF EXISTS dsjob;')
#cur.execute('CREATE DATABASE dsjob;')

#cur.execute("SELECT job_location,salary FROM indeed WHERE job_location LIKE '%Austin, TX%' AND salary LIKE '% a year';")
#cur.execute("SELECT job_location,salary FROM indeed WHERE salary LIKE '% a year';")


major_cities= [('New York','NY') , ('San Francisco','CA'), ('Seattle','WA'), 
    ('Chicago','IL'), ('Boston', 'MA'), ('Washington','DC'), ('Austin', 'TX'), 
    ('Atlanta','GA'), ('Los Angeles', 'CA'), ('Arlington', 'VA'), ('Dallas', 'TX'), ('Cambridge', 'MA'), 
    ('Houston', 'TX'), ('Mc Lean', 'VA')]


scrapped_job_counts=[]
for e in major_cities:
    city,state =e
    if city=='Mc Lean':
        city_search = 'McLean'
    else:
        city_search = city
    cur.execute("SELECT job_location,salary FROM indeed WHERE job_location LIKE %s;",['{}, {}%'.format(city_search, state)])
    counter = 0
    for item in cur.fetchall():
        counter+=1
    scrapped_job_counts.append(counter)

# plot the scraped job counts scraped from indeed.com
fig = plt.figure()
ax = fig.add_subplot()
width = 0.35
ind = np.arange(len(scrapped_job_counts))
s1 = ax.bar(ind, scrapped_job_counts, width, color = 'blue')
ax.set_ylabel('Job count')
ax.set_title('No. of jobs scraped by city')
ax.set_xticks(ind)
ax.set_xticklabels([ ", ".join(k) for k in major_cities])
ax.tick_params(axis = 'x', rotation = 80)
fig.tight_layout()
plt.show()



### plot each sample on a scatter plot of jobs has a annual salary with detailed description on indeed 
salary_indeed_sample_dict={}
for e in major_cities:
    city,state =e
    if city=='Mc Lean':
        city_search = 'McLean'
    else:
        city_search = city
    cur.execute("SELECT job_location,salary FROM indeed WHERE salary LIKE %s and job_location LIKE %s;",['% a year', '{}, {}%'.format(city_search, state)])
    l = []
    for item in cur.fetchall():
        l.append(average_salary(item[1]))
    print(city, state, np.round(np.mean(l)), len(l))
    salary_indeed_sample_dict[(city,state)]=l

fig, ax = plt.subplots()
for i, k in enumerate(salary_indeed_sample_dict): 
    for vv in salary_indeed_sample_dict[k]:
        ax.scatter(i, vv, color='b', alpha=0.2)
    print(k, salary_indeed_sample_dict[k])
    ax.scatter(i, np.mean(salary_indeed_sample_dict[k]), color ='r', marker='x')
ax.set_xticks(np.arange(len(salary_indeed_sample_dict)))
ax.set_xticklabels([", ".join(k) for k in salary_indeed_sample_dict.keys()])
ax.tick_params(axis = 'x', rotation = 80)
ax.set_title("Salary posted on Indeed job listings")
ax.set_ylabel("Salary")
fig.tight_layout()
plt.show()



#### Compute the average salary using the meta data from refine search result on indeed.com
d ={}
for e in major_cities:
    city, state = e
    cur.execute("SELECT * FROM refine_result2 WHERE by_category = 'by_salary' and city = %s and state = %s", [city,state])
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


### Read in living_cost of each city and adjust salary by cost of living index
cur.execute("SELECT * FROM living_cost")
living_cost_list = []
living_cost_dict={}
for item in cur.fetchall():
    city, state, score = item
    if (city, state) in major_cities:
        salary_avg = d[(city, state)]
        d[(city, state)] = (salary_avg, int(salary_avg*100/score)) 
        living_cost_list.append(score)
        living_cost_dict[(city,state)] = score


### convert the salary before and after adjustmnt to lists for plot
d_list = [(k, d[k][0], d[k][1]) for k in d]
city_list = [" ,".join(e) for e,_,_ in d_list]
salary_list = [e for _,e,_ in d_list]
disc_salary_list = [e for _,_,e in d_list]


##### Plot the salary before and after adjustment based on meta data on indeed.com
ind = np.arange(len(city_list))
width=0.35
fig = plt.figure()
ax = fig.add_subplot()

s1 = ax.bar(ind, salary_list, width, color = 'blue')
s2 = ax.bar(ind+width, disc_salary_list, width, color = 'r')


ax.set_ylabel('Salary')
ax.set_title('Salary estimated by Indeed')
ax.set_xticks(ind)
ax.set_xticklabels(city_list)
ax.tick_params(axis = 'x', rotation = 80)
ax.legend((s1,s2) ,  ('Salary estimated by Indeed', 'Salary estimated by Indeed with living cost adjustment'))

fig.tight_layout()
plt.show()




'''
#### Read in glassdoor living cost
cur.execute("SELECT * FROM glassdoor")
glassdoor_d = {}
for item in cur.fetchall():
    city, salary = item
    glassdoor_d[city] = salary 
glassdoor_salary_list = [glassdoor_d[location[0]] for location,_,_ in d_list ]
glassdoor_salary_disc_list = [int(e*100/c) for e,c in zip(glassdoor_salary_list, living_cost_list)]
print(glassdoor_salary_list)

##### plot the salary before and after adjustment using the mean salary from glassdoor.com
fig = plt.figure()
ax = fig.add_subplot()
s3 = ax.bar(ind, glassdoor_salary_list, width, color = 'cyan')
s4 = ax.bar(ind+width, glassdoor_salary_disc_list, width, color = 'plum')

ax.set_ylabel('Salary')
ax.set_title('Salary estimated by Glassdoor')
ax.set_xticks(ind)
ax.set_xticklabels(city_list)
ax.tick_params(axis = 'x', rotation = 80)
ax.legend((s3,s4) ,  ('Salary estimated by Glassdoor', 'Salary estimated by Glassdoor with living cost adjustment'))
fig.tight_layout()
plt.show()
'''

#### Pool the salary of job with detailed description on indeed to two groups:  
#from Texas and outside Texas
a=[]
b=[]
for i, k in enumerate(salary_indeed_sample_dict):
    if k[1] == 'TX':
        a = a + [e*100/living_cost_dict[k] for e in salary_indeed_sample_dict[k]]
    else:
        b = b + [e*100/living_cost_dict[k] for e in salary_indeed_sample_dict[k]]

print("list of adjusted salary from cities in texas:", a)
print("list of adjusted salaries from cities outside texas:", b)

#### plot the hisogram of two groups together
#plt.style.use('ggplot')
fig,ax = plt.subplots()
bins = np.linspace(10000, 250000, 15)
h1 = ax.hist(a, bins, alpha=0.5, edgecolor='r', linewidth = 1.2, label="TX")
h2 = ax.hist(b, bins,  alpha=0.5, edgecolor ='blue', linewidth = 1.2, label="Outside TX")
#h1[1].set_label("111")
#h2[1].set_label("222")
ax.set_title("Histogram of salaries from Indeed listing")
ax.set_ylabel("Job count")
ax.set_xlabel("Salary after living cost adjustment")
#plt.legend((h1,h2),("TX", "Outside TX"))
ax.legend()
plt.show()


#### Compute for variance of two group
print("Variance of list in Texas: ", np.var(a))
print("Variance outside Texas:", np.var(b))

#### QQ plot to check normaility of two groups (in and out of Texas)
fig,ax = plt.subplots()
res = probplot(a, dist='norm', plot=plt)
ax.set_title("Probplot for adjuted salary in Texas")
plt.show()

fig, ax = plt.subplots()
res = probplot(b, dist='norm', plot=plt)
ax.set_title("Probplot for adjuted salary outside Texas")
plt.show()


##### Two sample t test for two groups
t, p = ttest_ind(a, b, equal_var=False)
print("ttest_ind:            t = %g  p = %g" % (t, p))

#ttest_ind:            t = 5.71367  p = 1.97862e-06
# one tail p = p/2

t, p = ttest_ind([e-30000 for e in a], b, equal_var=False)
print("ttest_ind 30k:            t = %g  p = %g" % (t, p))
t, p = ttest_ind([e-32000 for e in a], b, equal_var=False)
print("ttest_ind 32k:            t = %g  p = %g" % (t, p))
t, p = ttest_ind([e-33000 for e in a], b, equal_var=False)
print("ttest_ind 33k:            t = %g  p = %g" % (t, p))
t, p = ttest_ind([e-33000 for e in a], b, equal_var=False)
print("ttest_ind 34k:            t = %g  p = %g" % (t, p))
t, p = ttest_ind([e-35000 for e in a], b, equal_var=False)
print("ttest_ind 35k:            t = %g  p = %g" % (t, p))
t, p = ttest_ind([e-40000 for e in a], b, equal_var=False)
print("ttest_ind 40k:            t = %g  p = %g" % (t, p))

##95% confidence interval for difference of sample mean of two groups
cm = sms.CompareMeans(sms.DescrStatsW(a), sms.DescrStatsW(b))
print (cm.tconfint_diff(usevar = 'unequal'))







