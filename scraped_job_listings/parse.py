from bs4 import BeautifulSoup

all_lines=[]
new_job_line_no=[]

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
    job_page=all_lines[new_job_line_no[e]: new_job_line_no[e+1]]
    soup = BeautifulSoup("".join(job_page), 'html.parser')
    url = soup.find("meta",  id="indeed-share-url")
    #print(url["content"] if url else "No meta url given")
    jk = url["content"].split("=")[-1]
    job_jk_set.add(jk)
#<meta content="http://www.indeed.com/viewjob?from=appsharedroid&amp;jk=e027cead9c01d424" id="indeed-share-url">
    salary = soup.find('span', {'class':'icl-u-xs-mr--xs'})
    if(salary):
        job_with_salary_counter+=1
    print(salary.get_text() if salary else "No salary given")
#<span class="icl-u-xs-mr--xs">$138,000 - $174,000 a year</span>
    title = soup.find('title')
    position_location = title.string.split("-")[-2].strip()
    position_title = "".join(title.string.split("-")[0:-2]).strip()
    print(title.string if title else "No title")
    print(position_title)
    print(position_location)


print(job_with_salary_counter)
print(len(job_jk_set))
'''
for i in new_job_line_no
        newjob.append(line)
            line = BeautifulSoup(f.read(), 'html.parser')
            titles = line.findAll('title')
    print([i.string for i in titles])
'''