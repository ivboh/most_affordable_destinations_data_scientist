import urllib.request
from bs4 import BeautifulSoup
#from selenium import webdriver
#import selenium
import time
import numpy as np
import io

'''
Scrape the jobs by states in addition to
the jobs already scraped nationwide
'''
def getjk(onelinestr):
    anchor ="jobKeysWithInfo['"
    if anchor in onelinestr:
        jobjk = onelinestr.replace("jobKeysWithInfo['", "").replace("'] = true;", "").rstrip()
        return jobjk
    else:
        return None

def alljk(inp):

    '''
    input a string (a string of a file or )
    return a set of strings where each element
    is a job's unique JK number that appeared in the file
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

def savejkbystate(state):
    '''
    Save all the pages of search result of given state
    with start+=50 for each page, and looping stops when all the job jk are posted on previous pages
    due to indeed.com will return a previous page for start number out of boundary
    return a set of string where each string is a unique job jk number
    '''
    result=set()
    ff=open("joblisting_{}.txt".format(state), 'w+')
    logff = open("job_counts_by_state.txt", 'a')
    consecutiveduplicatedpage =0 
    for start in range(0,100000,50):
        URL = "https://www.indeed.com/jobs?q=%28%22data+science%22+or+%22data+scientist%22%29&l={}&sort=date&limit=50&filter=0&start={}".format(state, start)
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
            ff.write(str(soup))
        print("state = {}, jobcounting={}".format(state, len(result)))
        logff.write("state = {}, jobcounting={}".format(state, len(result)))
    ff.close()
    logff.close()


def scrape_living_cost_page(city, state):
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
    ('Houston', 'TX'), ('Mc Lean', 'VA')]

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
