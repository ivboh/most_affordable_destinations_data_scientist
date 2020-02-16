# The Most Affordable Destination for Data Scientists?

<img src="https://github.com/ivboh/most_affordable_destinations_data_scientist/blob/master/img/title.png">

__Abstract:__
This project aimed to compare the average salary for data scientists with living cost adjustment. 14000+ job listings by Jan 02 2020 and the cost of living index were web scraped. A two sample t-test and furthermore an A/B test were applied to compare the salaries in Texas and in other states.

__Conclusion:__
The salaries after adjustment are (highly significantly) higher for DS in Texas than in other states. An A/B test at 0.05 significance level showed that the adjusted salary in Texas is $34,000 higher than in other states. That's saying a salary increase of $34,000 should break even when data scientists move from Texas to another state.

---
# Intruduction: background and motivation 
We hear data scientist friends relocate for new oppotunaties. The decision making process is complicated, from being able to watch broadway shows every week, to work with the smartest people. And one factor is often considered: the living cost. The goal of this project is to find the most affordable places to live for DS and the amount of lift if there is a winning city.

---
# Hypothesis and test

### Initial hypothesis
The original hypothesis I'd like to test was there is the one city more affordable than any other ones, however only ~300 job posts (~2%) scraped had a salary posted on it. Looking at the sample size for each city, the sparsity of data collected for a single city is problematic as 9/15 major cities have fewer than 10 samples. Few data samples will fail the normality assumption for the hypothesis of two sample t-test. As a result the data collected by city were pooled and grouped into Texas and non-Texas after initial exploratory data analysis. The new hypothesis was fomulated as the average salary for DS are higher in Texas than in other states. <img src = "https://github.com/ivboh/data_science_positions/blob/master/img/salary_posted_on_indeed_listing.png">

### Exploratory Data Analysis
The salary after adjustment is calculated as dividing the listed salary by the living cost index, e.g. if the salary is $100,000 on the job listing and the cost of living index is 200, the salary after adjustment is calculated as $100,000/200% = $50,000. The initial EDA showed the cities in Texas are similar both in salary range and living cost, and Austin, Dallas and Houston came out top with highest adjusted salaries. Therefore the data from Texas is pooled together vs in other states. 

### Final hypothesis

- Texas vs other states
The null hypothesis is that the mean salary are equal in Texas and outside Texas and the alternative hypothesis is that the average adjusted salary in Texas is higher than that in other states.
  
- How much is the lift
A confidence interval is constructed for the difference of average salary. And an A/B test confirmed the lift is significant.  

---
# Result
The cities in Texas are extremely significantly more affordable for data scientists than those in other states with a ```p value = 10e-06``` . A 95% condidence inteval for the difference of mean salaries in and out Texas is ```$31k to $65k```. 

An A/B test of signicicance level ```alpha = 0.05``` confirms that the adjusted salary in Texas is ```$34,000``` higher than the salaries outside Texas.

- <img src= "https://github.com/ivboh/data_science_positions/blob/master/img/hist_indeed_posted_salary_tx_vs_outside.png">


---
# Analysis flow and code
1. A list of top cities for DS jobs are found on ```indeed.com```  <img src="https://github.com/ivboh/data_science_positions/blob/master/img/list_of_cities_indeed_job_search.PNG"> 


2. Job listings were web scraped, parsed with Beautifulsoup and saved to a ```PostgreSQL``` data base as ```TABLE indeed``` with ```python indeed_job_jk_list_scraper.py``` <img src="https://github.com/ivboh/data_science_positions/blob/master/img/job_listing_example_indeed.PNG">


3. The cost of living index is scraped from ```areavibes.com```, parsed and added to the database as ```TABLE living_cost``` with  ```python areavibes_living_cost_scraper.py```


4. Metadata of job listings and salary brackets on ```indeed.com``` were scraped to add more information for initial EDA.  The information is saved as ```TABLE refine_result2``` with ```python indeed_refine_search_metadata_scraper.py```<img src= "https://github.com/ivboh/data_science_positions/blob/master/img/austin_indeed_refine_result_salary.PNG">


5. Initial EDA and all the statistical analysis, tests and plots were created with ``python analysis_sql.py```


---
# Data source and tools

### Data source
- indeed.com
- areavibes.com
- glassdoor.com
- nerdwallet.com
### Tools
- Web scraper on AWS EC2
- BeautifulSoup web parser
- Postgres data base
- Python libraries for EDA and statistical testing
  
---
# Data quality  
### Data consistency
- The average salaries was obtained in three ways: i) and iii) are more consistent. ii) has the most samples and iii) has one number for each city. The final statistical testing used samples from i)
  1. taking the mean of salary posted on the web page for a single job on indeed.com
  2. taking the mean of metadata of salary in refined search results on indeed.com
  3. taking the number from glassdoor.com

- The cost of living index from areavibes.com is calcuated using reliable methodology and is comparible with nerdwallet.com 

### Number of samples
- The number of pooled samples in and out of Texas are good (>30)
- <img src= "https://github.com/ivboh/data_science_positions/blob/master/img/salary_5mile_estimated_by_indeed.png">

### Normality of samples
- QQ plot verified that the samples in and out of Texas can be modeled by normal distribution. KS tests can be applied if p-value is needed.
- <img src="https://github.com/ivboh/data_science_positions/blob/master/img/qq_plot_of_salary_texas.png">
- <img src="https://github.com/ivboh/data_science_positions/blob/master/img/qq_plot_of_salary_outside_texas.png">


---
# Future work

- Take other factors into consideration: weather since not everyone can survive the Texas heat in summer, amenities, crime and school district rating for example.

- Study the correlation of key words: job qualification, responsibilities, companies and industry. 

---
# Acknowledgements 
I'd like to thank Joseph Gartner, Dan Rupp and Brent Goldberg for their guidance, feedback and technical support for this project.



