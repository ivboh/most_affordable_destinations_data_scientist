import urllib.request
from bs4 import BeautifulSoup
#from selenium import webdriver
#import selenium
import time
import numpy as np
import io
#from uszipcode import SearchEngine
import re

import psycopg2 as pg2

    
conn = pg2.connect(dbname='dsjob', host='localhost',
                    password='docker', user='postgres')
conn.autocommit = True
cur = conn.cursor()

#cur.execute('DROP TABLE IF EXISTS refine_result2;')
query='''CREATE TABLE IF NOT EXISTS refine_result2 (
            city varchar(50) NOT NUll,
            state varchar(2) NOT NULL,
            by_category varchar(50) NOT NULL,
            category varchar(50) NOT NULL,
            counts int NOT NULL,
            PRIMARY KEY (city, state, by_category, category)
        );'''
cur.execute(query)
cur.execute("ALTER TABLE refine_result2 ALTER category TYPE varchar(100);")


conn.commit()
'''
Scrape the jobs by states in addition to
the jobs already scraped nationwide
'''
def find_all_valid_zipcode():
    zipsearch = SearchEngine(simple_zipcode=True)
    l=[]
    for i in range(500, 100000):
        temp = zipsearch.by_zipcode(str(i).zfill(5))
        if temp.zipcode: l.append(temp.zipcode) 
    return l

def find_zipcode_in_major_states(major_states):
    '''
    input is list of string, each string is an abbreviation of a state
    return a list of string of zipcode for all the states in the input
    e.g. find_zipcode_in_major_states(['NY' , 'CA', 'WA', 'IL', 'DC', 'TX', 'GA', 'VA'])
    '''
    zipsearch = SearchEngine(simple_zipcode=False)
    l=[]
    for i in range(500, 100000):
        temp = zipsearch.by_zipcode(str(i).zfill(5))
        if temp.zipcode and temp.state in major_states: l.append(temp.zipcode) 
    return l

def find_zipcode_in_major_cities(major_cities):
    '''
    input is list of tuples, each tuple is pair of the name of the city and the state.
    return a list of string of zipcode for the cities in the input
    e.g. find_zipcode_in_major_states([('New York','NY') , ('San Francisco','CA'), ('Seattle','WA'), 
    ('Chicago','IL'), ('Boston', 'MA'), ('Washington','DC'), ('Austin', 'TX'), 
    ('Atlanta','GA'), ('Los Angeles', 'CA'), ('Arlington', 'VA'), ('Dallas', 'TX'), ('Cambridge', 'MA'),
    ('Houston', 'TX'), ('Mc Lean', 'VA')])
    '''   
    zipsearch = SearchEngine(simple_zipcode=False)
    l=[]
    for i in range(500, 100000):
        temp = zipsearch.by_zipcode(str(i).zfill(5))
        if temp.zipcode and (temp.city,temp.state) in major_cities: l.append((temp.zipcode, temp.city, temp.state)) 
    return l

    

def getjk(onelinestr):
    anchor ="jobKeysWithInfo['"
    if anchor in onelinestr:
        jobjk = onelinestr.replace("jobKeysWithInfo['", "").replace("'] = true;", "").rstrip()
        return jobjk
    else:
        return None

def alljk(inp):

    '''
    input: a string or a file
    return: a set of job JK number
    '''
    l=set()
    if isinstance(inp, str):
        for line in inp.split('\n'):
            #print (line)
            jobjk = getjk(line)
            if not jobjk == None:
                l.add(jobjk)
        return l
    if isinstance(inp, io.IOBase):
        for line in inp:
            jobjk = getjk(line)
            if not jobjk == None:
                l.add(jobjk)
        return l


def isscraped(jk, jkset):
    return True if jk in jkset else False

def scrape(jk, f):
    '''
    scrape webpage of job listing with jk number to file f.
    '''
    time.sleep(np.random.randint(5, 10))
    URL = "https://www.indeed.com/viewjob?jk={}".format(jk)
    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')
    f.write(str(soup))

def savejkbylocation(zipcode):
    '''
    Save all the pages of search result of given location
    with start+=50 for each page, and looping stops when all the job jk are posted on previous pages
    due to indeed.com will return a previous page for start number out of boundary
    return a set of string where each string is a unique job jk number
    '''
    result=set()
    ff=open("joblisting_zipcode.txt", 'a')
    logff = open("job_counts_by_zipcode.txt", 'a')
    consecutiveduplicatedpage = 0 
    for start in range(0,100000,50):
        URL= 'https://www.indeed.com/jobs?q=("data+science"+or+"data+scientist")&l={}&jt=fulltime&radius=10&filter=0&limit=50&start={}'.format(zipcode,start)
        print (str(URL))
        time.sleep(np.random.randint(5,15))
        soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')
        jkset_this_page=alljk(str(soup))
        if all(x in result for x in jkset_this_page): 
        # exit looping if the page is a duplicate
            ff.close()
            logff.close()
            return result
        else:
            result=result.union(jkset_this_page)
            for e in jkset_this_page:
                ff.write(zipcode+","+str(e)+'\n')
        print("zipcode = {}, jobcounting={}".format(zipcode, len(result)))
        logff.write("zipcode = {}, jobcounting={}".format(zipcode, len(result)))
    ff.close()
    logff.close()
    return result

def save_counts_salary_by_city(city, state):
    time.sleep(np.random.randint(30,50))
    URL = 'https://www.indeed.com/jobs?q=(%22data+science%22+or+%22data+scientist%22)&l={},+{}'.format(city,state)
    print(URL)
    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')    
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

  
    e = soup.findAll('div', {'id':'rb_Company'}) #find('div', {'id':'refineresults'})
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

    return {'by_salary': refine_by_salary, 
            'by_jobtype':refine_by_jobtype,
            'by_company': refine_by_company}

def save_counts_salary_by_city2(city, state):
    time.sleep(np.random.randint(30,50))
    URL = 'https://www.indeed.com/jobs?q=(%22data+science%22+or+%22data+scientist%22)&l={},+{}&radius=5'.format(city,state)
    print(URL)
    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')    
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

  
    e = soup.findAll('div', {'id':'rb_Company'}) #find('div', {'id':'refineresults'})
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

    return {'by_salary': refine_by_salary, 
            'by_jobtype':refine_by_jobtype,
            'by_company': refine_by_company}

def savejkbycity(city, state, exp_level):
    '''
    Save all the pages of search result of given location
    with start+=50 for each page, and looping stops when all the job jk are posted on previous pages
    due to indeed.com will return a previous page for start number out of boundary
    return a set of string where each string is a unique job jk number
    '''
    result=set()
    city = "+".join(city.split(" "))
    ff=open("joblisting_{}_{}_{}.txt".format(city,state,exp_level), 'a')
    logff = open("job_counts_by_city.txt", 'a')
    consecutiveduplicatedpage = 0 
    for start in range(0,100000,50):
        URL = 'https://www.indeed.com/jobs?q=(%22data+science%22+or+%22data+scientist%22)&l={},+{}&jt=fulltime&explvl={}&radius=25&limit=50&filter=0&start={}'.format(city,state, exp_level,start)
        print (str(URL))
        time.sleep(np.random.randint(10,15))
        soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')
        jkset_this_page=alljk(str(soup))
        if all(x in result for x in jkset_this_page): 
        # exit looping if the page is a duplicate
            ff.close()
            logff.close()
            return result
        else:
            result=result.union(jkset_this_page)
            for e in jkset_this_page:
                ff.write("{} {} {},".format(city, state, exp_level)+str(e)+'\n')
        print("{},{},{}, jobcounting={}".format(city,state,exp_level,len(result)))
        logff.write("{},{},{}, jobcounting={}".format(city,state,exp_level,len(result)))
    ff.close()
    logff.close()
    return result

'''
scraped_f = open("joblisting.txt", "r+")
all_job_scraped = alljk(scraped_f)
scraped_f.close()
'''

##### stage 0: search for job summary in listing 
major_cities= [('New York','NY') , ('San Francisco','CA'), ('Seattle','WA'), 
    ('Chicago','IL'), ('Boston', 'MA'), ('Washington','DC'), ('Austin', 'TX'), 
    ('Atlanta','GA'), ('Los Angeles', 'CA'), ('Arlington', 'VA'), ('Dallas', 'TX'), ('Cambridge', 'MA'),
    ('Houston', 'TX'), ('Mc Lean', 'VA'), ('Redwood City', 'CA'), ('Mountain View', 'CA')]
cur.execute("SELECT DISTINCT(city) FROM refine_result2;")
scrapped_cities = [item[0] for item in cur]
print(scrapped_cities)
#major_citiest= major_cities[1:]
#major_cities = [major_cities[0]]
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

#### stage I :search all the data science job listings by state without saving job description
# dict = {}
# for state in states:
#     dict[state] = savejkbylocation(state)
#l = find_all_valid_zipcode()



'''    
l=find_zipcode_in_major_cities(major_cities)
f=open('zipcode_of_major_cities.txt', 'w+')
for zipcode in l:
    f.write(str(zipcode)+'\n')
f.close()

with open('zipcode_of_major_cities.txt', 'r+') as f:
    for line in f:
        zipcode, city, state = line.replace("(","").replace(")","").split(",")
        print(zipcode,city,state)
        if (int(zipcode.replace("'","")) >= 2212):
            savejkbylocation(zipcode) 

exp_levels=["entry_level","mid_level","senior_level"]

for e in major_cities:
    city, state = e
    for exp_level in exp_levels:
        savejkbycity(city, state, exp_level)



#### stage II: save each job description of all states if the job is not scraped
#switchon = False
parsed_jk_set=set()
with open('parsed_db_by_states.txt', 'r+') as f:
    for line in f:
        parsed_jk_set.add(line.rstrip())
    


for e in major_cities:
    city, state = e
    city = "+".join(city.split(" "))
    for exp_level in exp_levels:
        f_summary=open("major_city_job_summary_{}_{}_{}.txt".format(city,state,exp_level), 'w+')
        f_log = open("log_scrape_by_city.txt",'a')
        with open("joblisting_{}_{}_{}.txt".format(city,state,exp_level), 'r+') as f:
            for line in f:
                location, jk = line.rstrip().split(",")
                if not jk in parsed_jk_set: 
                    scrape(jk, f_summary)
                    f_log.write(str(location)+","+jk+'\n')
                    print(location+","+jk+'\n')
                else:
                    print("skip location = {}, jk = {} scraped ", location, jk)
        f_summary.close()
f_log.close()


f = open("job_summary_by_states_compliment.txt" , 'w+')
logf = open("logf_by_states.txt", 'w+')
by_states_job_summary_scraped = 0
for state in states:
    state_f = open("joblisting_{}.txt".format(state), 'r+')
    state_jkset = alljk(state_f)
    state_f.close()
    for jk in state_jkset:
        print("jk = {}".format(jk))
        if isscraped(jk, all_job_scraped):
            print("already scraped job = {}, state = {}".format(jk,state))
        elif (not isscraped(jk, all_job_scraped)): #and switchon
            scrape(jk, f)
            by_states_job_summary_scraped+=1
            print("scrape job = {}, state = {}".format(jk,state))
            logf.write("scrape job = {}, state = {}".format(jk,state))
        #if jk=="22e9e9d55703c63d":
        #    switchon = True
f.close()
logf.close()

'''


'''
######### phase II
anchor = "jobKeysWithInfo['"
#start = 0
start = 0
last_tag_line_no = None
f = open('job_summary_listing_single_page.txt', 'w+')
logf = open('logfile.txt', 'w+')
total_summary = 0
for i, line in enumerate(open('joblisting.txt')):
    if anchor in line:
        total_summary+=1
        if last_tag_line_no ==None:
            last_tag_line_no = i
        if (i-last_tag_line_no)>2:
            start+=50
        result = line.replace("jobKeysWithInfo['", "").replace("'] = true;", "")
        print("start= {},  line_no = {}, total_summary={}".format(start, i, total_summary))
        print(result)
        if (total_summary <=3131 ):
            #if total_summary>0 and total_summary%1000==0:
            #    f.close()
            #    f=open('job_summary_list_{}.txt'.format(total_summary) , 'w+')
            time.sleep(np.random.randint(5, 10))
            URL = "https://www.indeed.com/viewjob?jk={}".format(result)
            #URL = "https://www.indeed.com/jobs?q=(%22data%20science%22%20or%20%22data%20scientist%22)&sort=date&limit=50&filter=0&radius=25&start="+str(start)+"&vjk="+result
            #URL = "https://www.indeed.com/jobs?q=(\"data science\" or \"data scientist\")&sort=date&limit=50&filter=0&radius=25&start={}&vjk={}".format(start, result)
            soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')
            f.write(str(soup))
            logf.write("start= {},  line_no = {}, total_summary = {}".format(start, i, total_summary))
        last_tag_line_no = i
f.close()
'''

'''
driver = webdriver.Chrome("./chromedriver")
#links = driver.find_elements_by_xpath("//div[@class='title']/a")
driver.get(URL)

#dismiss = driver.find_elements_by_class_name('tos-Button tos-Button-white')
#dismiss.click()


all_jobs = driver.find_elements_by_class_name('title')
for e in all_jobs:
    #time.sleep(np.rand.randint(5, 15))
    print(e)
'''

'''
print(all_jobs)

for job in all_jobs:
    result_html = job.get_attribute('innerHTML')
    soup = BeautifulSoup(result_html, 'html.parser')
    try:
        title = soup.find("a", class_="title ").text.replace("\n","").strip()
    except:
        title = None
    try:
        location = soup.find("a", class_="location").text.replace("\n","").strip()
    except:
        location = None
    try:
        company = soup.find("a", class_="company").text.replace("\n","").strip()
    except:
        company = None
    try:
        salary = soup.find("a", class_="salary").text.replace("\n","").strip()
    except:
        salary = None
    try:
        sponsored = soup.find("a", class_="sponsoredGray").text
        sponsored = "Sponsored"
    except:
        title = "Organic"
    summary_div = job.find_elements_by_class_name("summary")[0]
    
    #summary_div.click()
    job_desc = driver.find_element_by_id("vjs-desc").text
   # print(title + location + company + salary + sponsored + job_desc)
    print(title)

'''
