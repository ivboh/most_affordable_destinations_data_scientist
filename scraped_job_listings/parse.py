from bs4 import BeautifulSoup
import os
import re

all_lines=[]
new_job_line_no=[]

'''
directory = os.fsencode('data')
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.startswith("job_summary"):
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
    soup = BeautifulSoup("".join(job_page_list_of_lines), 'html.parser')

#<meta content="http://www.indeed.com/viewjob?from=appsharedroid&amp;jk=e027cead9c01d424" id="indeed-share-url">
    url = soup.find("meta",  id="indeed-share-url")
    #print(url["content"] if url else "No meta url given")
    jk = url["content"].split("=")[-1] if url else "No jk"
    job_jk_set.add(jk)

#<span class="icl-u-xs-mr--xs">$138,000 - $174,000 a year</span>
    salary = soup.find('span', {'class':'icl-u-xs-mr--xs'})
    if salary:job_with_salary_counter+=1
    
    title = soup.find('title')
    position_location = title.string.split("-")[-2].strip() if title else "No title"
    position_title = "".join(title.string.split("-")[0:-2]).strip() if title else "No title"
    
    company_info = soup.findAll('div', {'class':'icl-u-lg-mr--sm icl-u-xs-mr--xs'})
    if company_info: company_info_string= "".join([temp.get_text().replace("-","") for temp in company_info])
    
    #### This method returns nothing
    # job_description = soup.find('div', {'class':'jobsearch-jobDescriptionText'})
    # if job_description: job_description_string=job_description.get_text()
    
    
    for i, line in enumerate(job_page_list_of_lines):
        if "jobsearch-jobDescriptionText" in line : job_description_firstline=i+1
        if "mosaic-zone-belowJobDescription" in line: job_description_lastline=i

    print(title.string if title else "No title")
    print(position_title)
    print(position_location)
    print(salary.get_text() if salary else "No salary given")
    print(company_info_string if company_info else "No company info")
    for line in job_page_list_of_lines[job_description_firstline:job_description_lastline]:
        print(re.sub('<[^>]+>', '', line))



print(job_with_salary_counter)
print(len(job_jk_set))
'''
for i in new_job_line_no
        newjob.append(line)
            line = BeautifulSoup(f.read(), 'html.parser')
            titles = line.findAll('title')
    print([i.string for i in titles])
'''