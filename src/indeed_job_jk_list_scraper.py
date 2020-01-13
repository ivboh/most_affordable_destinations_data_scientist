import urllib.request
from bs4 import BeautifulSoup
import time
import numpy as np
import io
import re
import psycopg2 as pg2    

def getjk(onelinestr):
    '''
    Find the unique job jk number of one line from the search result page
    Input : a string (one line on the webpage as a string)
    Return: the jobjk number if exists, other wise return None
    '''

    anchor ="jobKeysWithInfo['"
    if anchor in onelinestr:
        jobjk = onelinestr.replace("jobKeysWithInfo['", "").replace("'] = true;", "").rstrip()
        return jobjk
    else:
        return None

def alljk(inp):

    '''
    This function gets a set of job JK numbers from the input file or input string
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
    '''
    This function finds if a jobjk as a string already in the set jkset 
    '''
    return True if jk in jkset else False

def scrape(jk, f):
    '''
    scrape webpage of job listing with jk number to file f.
    '''
    time.sleep(np.random.randint(5, 10))
    URL = "https://www.indeed.com/viewjob?jk={}".format(jk)
    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')
    f.write(str(soup))

def savejkbycity(city, state, exp_level):
    '''
    Save all the pages of search result of given location
    with start+=50 for each page, and looping stops when all the job jk are posted on previous pages
    due to indeed.com will return a previous page for start number out of boundary
    return a set of string where each string is a unique job jk number
    Input:
            e.g. savejkbycity("Austin", "TX", "entry_level")
    Return: a set with each element as a string
            e.g. {"71e51bebecc5cab0",
                    "e51e46c5830b30dd",
                    "a9de383e2857c0fb",
                    "d288b661d6cc532f",
                    "d712f6814eca0ef0",
                    "507f58ce2ce83acc",
                    "1ec56ae06c7a20f0"}
    The function also writes the job ids to file with name joblisting_city_state_exp_level.txt
            e.g. writes
            "Austin TX entry_level,71e51bebecc5cab0
                Austin TX entry_level,e51e46c5830b30dd
                Austin TX entry_level,a9de383e2857c0fb
                Austin TX entry_level,d288b661d6cc532f
                Austin TX entry_level,d712f6814eca0ef0
                Austin TX entry_level,507f58ce2ce83acc
                Austin TX entry_level,1ec56ae06c7a20f0" 
             to file 
             "joblisting_Austin_TX_entry_level.txt"


    '''

    result=set()
    city = "+".join(city.split(" "))
    ff=open("joblisting_{}_{}_{}.txt".format(city,state,exp_level), 'a')
    logff = open("job_counts_by_city.txt", 'a')
    consecutiveduplicatedpage = 0 
    for start in range(0,100000,50):
        URL = 'https://www.indeed.com/jobs?q=(%22data+science%22+or+%22data+scientist%22)&l={},+{}&jt=fulltime&explvl={}&radius=25&limit=50&filter=0&start={}'.format(city,state, exp_level,start)
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
                ff.write("{} {} {},".format(city, state, exp_level)+str(e)+'\n')
        print("{},{},{}, jobcounting={}".format(city,state,exp_level,len(result)))
        logff.write("{},{},{}, jobcounting={}".format(city,state,exp_level,len(result)))
    ff.close()
    logff.close()
    return result


#### stage I :search for data science position for each city and experience level 
#### and save the webpages to a text file
major_cities = [('New York','NY') , ('San Francisco','CA'), ('Seattle','WA'), ('Chicago','IL'), 
                ('Boston', 'MA'), ('Washington','DC'), ('Austin', 'TX'), ('Altlanta','GA'),
                ('Los Angeles', 'CA'), ('Arlington', 'VA'), ('Dallas', 'TX'), ('Cambridge', 'MA'),
                ('Houston', 'TX'), ('Mc Lean', 'VA')]
exp_levels=["entry_level","mid_level","senior_level"]

for e in major_cities:
    city, state = e
    for exp_level in exp_levels:
        savejkbycity(city, state, exp_level)

#### stage II: scrape each job description by the unique JK number in saved joblisting file by city/state
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



##### stage III: read in all the files written in stage II and 
# save the job with detailed description in TABLE indeed

conn = pg2.connect(dbname='dsjob', host='localhost',
                    password='docker', user='postgres')
conn.autocommit = True
cur = conn.cursor()
cur.execute('DROP DATABASE IF EXISTS dsjob;')
cur.execute('CREATE DATABASE dsjob;')
cur.execute('DROP TABLE IF EXISTS indeed;')

query='''CREATE TABLE IF NOT EXISTS indeed (
            job_jk varchar(16) default NUll,
            job_title varchar(200) NOT NULL,
            job_location varchar(110) default NULL,
            company_name varchar(120) default NULL,
            salary varchar(130) default NULL,
            description text default NULL,
            PRIMARY KEY (job_jk)
        );'''
cur.execute(query)
conn.commit()

all_lines=[]
new_job_line_no=[]


directory = os.fsencode('data')
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.startswith("major_city_job_summary_"):
         #print(os.path.join(str(directory), filename))
         with open('data/'+filename) as f:
             print(filename)
             for line in f:
                 all_lines.append(line)
     else:
         continue

counter=0
new_job_line_no=[]
for line in all_lines:
    if 'html dir="ltr" lang="en"' in line:
            new_job_line_no.append(counter)
    counter+=1        
new_job_line_no.append(counter)


job_with_salary_counter=0
job_jk_set=set()


for e in range(len(new_job_line_no)-1):
    job_page_list_of_lines =all_lines[new_job_line_no[e]: new_job_line_no[e+1]]
    soup = BeautifulSoup(''.join(job_page_list_of_lines), 'html.parser')

    ### parse for job jK number
    #<meta content="http://www.indeed.com/viewjob?from=appsharedroid&amp;jk=e027cead9c01d424" id="indeed-share-url">
    url = soup.find('meta',  id='indeed-share-url')
    #print(url["content"] if url else "No meta url given")
    jk = url['content'].split('=')[-1].rstrip() if url else 'No jk'
    job_jk_set.add(jk)

    ### parse for job salary posted if any
    #<span class="icl-u-xs-mr--xs">$138,000 - $174,000 a year</span>
    salary = soup.find('span', {'class':'icl-u-xs-mr--xs'})
    if salary:job_with_salary_counter+=1
    salary_string = salary.get_text() if salary else "No salary given"

    ### parse for job title posted if any
    title = soup.find('title')
    position_location = title.string.split("-")[-2].strip() if title else "No title"
    position_title = "".join(title.string.split("-")[0:-2]).strip() if title else "No title"
    
    ### parase for company infomation if any
    company_info = soup.findAll('div', {'class':'icl-u-lg-mr--sm icl-u-xs-mr--xs'})
    company_info_string= "".join([temp.get_text().replace("-","") for temp in company_info]) if company_info else "No company info"
    
    ### parse for detailed job description
    for i, line in enumerate(job_page_list_of_lines):
        if "jobsearch-jobDescriptionText" in line : job_description_firstline=i+1
        if "mosaic-zone-belowJobDescription" in line: job_description_lastline=i+1
    job_description_list =[]
    for line in job_page_list_of_lines[job_description_firstline:job_description_lastline]:
        job_description_list.append(re.sub('<[^>]+>', '', line))
    job_description_string = "".join(job_description_list)


    print(jk)
    print(position_title)
    print(position_location)
    print(company_info_string)
    print(salary_string)
    print(job_description_string)

    ### save parsed information to data base TABLE indeed
    cur.execute("INSERT INTO indeed(job_jk, job_title, job_location,company_name, salary, description) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (job_jk) DO NOTHING",[jk, position_title, position_location,company_info_string,salary_string,job_description_string])    
    conn.commit()

cur.close()
conn.close()
