# The Most Affordable Destinations for Data Scientists?

<img src="http://alabamamaps.ua.edu/contemporarymaps/usa/basemaps/mjcityzmc.jpg">

__Abstract:__
This project is to find out the salary adjusted by the living cost at popular destinations for data scientists. I web scraped 14000+ job listings from indeed.com by Jan 02 2020, plus the cost of living index of cities in 2019 from areavibes.com. The analysis was done using two sample t-test, more specifically a A/B test to find out the lift between salaries in Texas and other states.

__Conclusion:__
The cities in Texas are (highly significantly) more affordable for data scientists than those in other states. An A/B test with significance level of 0.05 shows that the adjusted salary in Texas is $34,000 higher than the salaries outside Texas. The take home message: a data scientist need a salary rise at least $34,000 on average if move from Texas to another state.

---
# Intruduction: background and motivation: 
Occassionally I hear my data scientist friends relocate, or were unwilling to do so, for new oppotunaties. The decision making process varies greatly, from being able to watch broadway shows every week to working with the smartest people they know of. But one factor remains one of the concerns: the living cost at the new location. The goal of my project is to find out the most affordable place to live for data scientists and by which amount if there is a winner.

---
# Hypothesis and test:

### Initial hypothesis
The original hypothesis is that there is a city that's more affordable than any other city before the data was collected. It turned out that very few (~2%) job listings scraped from indeed posted salary for individual cities and I have less than 10 sample for half of cities.

### EDA:
EDA shows cities in Texas are similar in both salary and living cost, and all came out as winners. So I decide to pool data from Texas together and compare it to the rest of the states.

### Final hypothesis:

- Texas vs other states:
  The null hypothesis: Texas and other states have the same mean salary adjusted by living cost. The alternative hypothesis is that the average adjusted salary in Texas is higher than that in other states.
  
- How much is the lift:
  A confidence interval is constructed for the difference of average salaries in and out of Texas. And an A/B test was conducted to confirm the lift is significant.  


---
# Analysis flow and code:
1. A list of cities with most job listings from ```indeed.com``` is used as the major cities for data scientists 
2. Job listings are web scraped from ```indeed.com``` , parsed and save to a ```Postgress``` data base  using ```scrape.py``` as ``` TABLE indeed```
3. Cost of living index is scraped from ```areavibes.com```, parsed and add to the data base as ```TABLE living_cost```
4. Metadata of job listings at major cities on ```indeed.com``` and  ```glassdoor.com```  are also web scraped for assisting initial EDA  ```TABLE refine_result2```
5. Initial EDA was done ``analysis.py```
6. Two sample ```t-tesst``` , ```confidence inteval```  and  ```A\B test``` was done ```analysis.py```


---
# Result:
The cities in Texas are extremely significantly more affordable for data scientists than those in other states with a ```p value = 10e-06``` . A 90% condidence inteval for the difference of mean salaries in and out Texas is ```($30,000 to $54,000)```. 



An A/B test of signicicance level ```alpha = 0.05``` confirms that the adjusted salary in Texas is ```$34,000``` higher than the salaries outside Texas.


---
# Data source:

### Data source: 
indeed.com areavibes.com glassdoor.com
  

### Data quality  
 
  



---
# Future work:



### take other factors into consideration: 
amenities, crime, school and weather

### study the correlation of key words: 
job qualification, responsibilities and companies to find the most deployed technologies 

---
# Acknowledgements: I'd like to thank Joseph Gartner, Dan Rupp and Brent Goldberg for their guidance, feedback and technical support for this project.

# Web app:
TBA
