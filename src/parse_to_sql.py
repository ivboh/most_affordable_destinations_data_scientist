from bs4 import BeautifulSoup
import os
import re
import psycopg2 as pg2

conn = pg2.connect(dbname='dsjob', host='localhost',
                    password='docker', user='postgres')
conn.autocommit = True
cur = conn.cursor()
#cur.execute('DROP DATABASE IF EXISTS dsjob;')
#cur.execute('CREATE DATABASE dsjob;')
#cur.execute('DROP TABLE IF EXISTS indeed;')

# query='''CREATE TABLE IF NOT EXISTS indeed (
#             job_jk varchar(16) default NUll,
#             job_title varchar(200) NOT NULL,
#             job_location varchar(110) default NULL,
#             company_name varchar(120) default NULL,
#             salary varchar(130) default NULL,
#             description text default NULL,
#             PRIMARY KEY (job_jk)
#         );'''
# cur.execute(query)
# conn.commit()

all_lines=[]
new_job_line_no=[]


directory = os.fsencode('data')
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.startswith("major_city_job_summary_San+Francisco"):
         #print(os.path.join(str(directory), filename))
         with open('data/'+filename) as f:
             print(filename)
             for line in f:
                 all_lines.append(line)
     else:
         continue
'''
with open('data/job_summary_listing_single_page_1_3131.txt') as f:
    for line in f:
        all_lines.append(line)
'''
counter=0
new_job_line_no=[]
for line in all_lines:
    if 'html dir="ltr" lang="en"' in line:
            new_job_line_no.append(counter)
    counter+=1        
new_job_line_no.append(counter)


job_with_salary_counter=0
job_jk_set=set()


def parse_job_page():
    '''
    The input is a BeautifulSoup object
    '''
    return 


for e in range(len(new_job_line_no)-1):
    job_page_list_of_lines =all_lines[new_job_line_no[e]: new_job_line_no[e+1]]
    soup = BeautifulSoup(''.join(job_page_list_of_lines), 'html.parser')

#<meta content="http://www.indeed.com/viewjob?from=appsharedroid&amp;jk=e027cead9c01d424" id="indeed-share-url">
    url = soup.find('meta',  id='indeed-share-url')
    #print(url["content"] if url else "No meta url given")
    jk = url['content'].split('=')[-1].rstrip() if url else 'No jk'
    job_jk_set.add(jk)


#<span class="icl-u-xs-mr--xs">$138,000 - $174,000 a year</span>
    salary = soup.find('span', {'class':'icl-u-xs-mr--xs'})
    if salary:job_with_salary_counter+=1
    salary_string = salary.get_text() if salary else "No salary given"

    title = soup.find('title')
    position_location = title.string.split("-")[-2].strip() if title else "No title"
    position_title = "".join(title.string.split("-")[0:-2]).strip() if title else "No title"
    
    company_info = soup.findAll('div', {'class':'icl-u-lg-mr--sm icl-u-xs-mr--xs'})
    company_info_string= "".join([temp.get_text().replace("-","") for temp in company_info]) if company_info else "No company info"
    
    #### This method returns nothing
    # job_description = soup.find('div', {'class':'jobsearch-jobDescriptionText'})
    # if job_description: job_description_string=job_description.get_text()
    
    
    for i, line in enumerate(job_page_list_of_lines):
        if "jobsearch-jobDescriptionText" in line : job_description_firstline=i+1
        if "mosaic-zone-belowJobDescription" in line: job_description_lastline=i+1
    # print(title.string if title else "No title")
    # print(position_title)
    # print(position_location)
    # print(salary.get_text() if salary else "No salary given")
    # print(company_info_string if company_info else "No company info")
    job_description_list =[]
    for line in job_page_list_of_lines[job_description_firstline:job_description_lastline]:
        job_description_list.append(re.sub('<[^>]+>', '', line))
    job_description_string = "".join(job_description_list)

    # job_summary_full_string = ",".join([jk, position_title, salary_string,
    #                         position_location, company_info_string,
    #                         job_description_string])
    # print (job_summary_full_string)
    print(jk)
    print(position_title)
    print(position_location)
    print(company_info_string)
    print(salary_string)
    print(job_description_string)

    # query = '''INSERT INTO indeed(job_jk, job_title, job_location, company_name, salary, description)
    #                     VALUES
    #                     (jk, position_title, position_location,company_info_string,salary_string,job_description_string);'''
    # cur.execute(query)

    cur.execute("INSERT INTO indeed(job_jk, job_title, job_location,company_name, salary, description) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (job_jk) DO NOTHING",[jk, position_title, position_location,company_info_string,salary_string,job_description_string])    
    conn.commit()

cur.close()
conn.close()


'''
dbf = open( "parsed_db_by_states" ,"w+")  
for e in job_jk_set:    
    dbf.write(e+'\n')
dbf.close()


print(job_with_salary_counter)
print(len(job_jk_set))
'''