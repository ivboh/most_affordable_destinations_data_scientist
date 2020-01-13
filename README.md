# The Most Affordable Destinations for Data Scientists?

<img src="http://alabamamaps.ua.edu/contemporarymaps/usa/basemaps/mjcityzmc.jpg">

__Abstract:__
This project is to find out the salary adjusted by the living cost at popular destinations for data scientists. I web scraped 14000+ job listings from indeed.com by Jan 02 2020, plus the cost of living index of cities in 2019 from areavibes.com. The analysis was done using two sample t-test, more specifically a A/B test to find out the lift between salaries in Texas and other states.

__Conclusion:__
The cities in Texas are (highly significantly) more affordable for data scientists than those in other states. An A/B test with significance level of 0.05 shows that the adjusted salary in Texas is $34,000 higher than the salaries outside Texas. The take home message: a data scientist need a salary rise at least $34,000 on average if move from Texas to another state.

---
# Intruduction: background and motivation 
Occassionally I hear my data scientist friends relocated, or were unwilling to do so, for new oppotunaties. The decision making process is complecated and varies greatly, from being able to watch broadway shows every week to wanting to work with the smartest people they know of. But one factor remains a main concern: the living cost at the new location. The goal of my project is to find out the most affordable place to live for data scientists and by which amount if there is a winner.

---
# Hypothesis and test

### Initial hypothesis
The original hypothesis is that there is a city that's more affordable than any other city before the data was collected. It turned out that only a small portion (~2%) of job listings scraped from indeed posted salary for individual cities and less than 10 samples were collected for half of the cities, to one's disspointment.

### Exploratory Data Analysis
EDA shows cities in Texas are similar in both salary and living cost, and all came out as winners. The data from Texas is pooled together vs from outside.

### Final hypothesis

- Texas vs other states:the null hypothesis is Texas and other states have the same mean salary adjusted by living cost, hence the alternative hypothesis is that the average adjusted salary in Texas is higher than that in other states.
  
- How much is the lift:a confidence interval is constructed for the difference of average salaries in and out of Texas. And an A/B test was conducted to confirm the lift is significant.  


---
# Analysis flow and code
1. A list of cities with most job listings from ```indeed.com``` is used as the major cities for data scientists 
2. Job listings are web scraped from ```indeed.com``` , parsed and save to a ```Postgress``` data base as ```TABLE indeed``` if run ```python indeed_job_jk_list_scraper.py```
3. Cost of living index is scraped from ```areavibes.com```, parsed and add to the data base as ```TABLE living_cost``` if run ```python areavibes_living_cost_scraper.py``` <img src= "https://github.com/ivboh/data_science_positions/blob/master/img/austin_cost_of_living.PNG">
4. Metadata of job listings at major cities on ```indeed.com``` are web scraped to add more information for initial EDA.  The information is save in ```TABLE refine_result2``` if run ```python indeed_refine_search_metadata_scraper.py```
5. Salary after living cost adjustment uses salary divided by the cost of living index as percentage, i.e. if the salary is $100,000 and the cost of living index is 200,  the salary after adjustment if $100,000/222% = %50,000
6. Initial EDA and all the statistical analysis, tests and plots will be created if run ``python analysis_sql.py```


---
# Result
The cities in Texas are extremely significantly more affordable for data scientists than those in other states with a ```p value = 10e-06``` . A 95% condidence inteval for the difference of mean salaries in and out Texas is ```$31k to $65k```. 

An A/B test of signicicance level ```alpha = 0.05``` confirms that the adjusted salary in Texas is ```$34,000``` higher than the salaries outside Texas.


---
# Data source
- indeed.com
- areavibes.com
- glassdoor.com
- nerdwallet.com
  
  
---
# Data quality  
### Data consistency
- The mean salaries was obtained in three ways: i) and iii) are more consistent. ii) has the most samples and iii) has one number for each city. The final statistical testing used samples from i)
  1. taking the mean of salary posted on the web page for a single job on indeed.com
  2. taking the mean of metadata of salary in refined search results on indeed.com
  3. taking the number from glassdoor.com

- The cost of living index from areavibes.com is calcuated from multiple neighborhood in the cities. The index as a single score is a robust and reliable. The methodology for the calculation is comparible between areavibes.com and nerdwallet.com 
  

### Number of samples
- The number of pooled samples in and out of Texas are good (>30)
- <img src= "https://github.com/ivboh/data_science_positions/blob/master/img/hist_indeed_posted_salary_tx_vs_outside.png">

### Normality of samples
- QQ plot verified that the samples in and out of Texas can be modeled by normal distribution. KS tests can be applied if p-value is needed.
- <img src="https://github.com/ivboh/data_science_positions/blob/master/img/qq_plot_of_salary_texas.png">
- <img src="https://github.com/ivboh/data_science_positions/blob/master/img/qq_plot_of_salary_outside_texas.png">


---
# Future work

- Take other factors into consideration: Weather for example since not everybody can survive the Texas summer.
Other factors like amenities, crime and school district rating.

- Study the correlation of key words: Job qualification, responsibilities, companies and industry to find a correlation. 

---
# Acknowledgements 
I'd like to thank Joseph Gartner, Dan Rupp and Brent Goldberg for their guidance, feedback and technical support for this project.


---
# Reference:

---
# Web app
TBA
