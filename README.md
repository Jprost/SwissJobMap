# SwissEmploymentMap
After spending some time on LinkedIn, I felt that a map was missing to have
a clear and straight forward visualizations of the Swiss employment market.
This repo contains the data (scrapped) and the code to build an interactive web app.
The page contains a map and four charts to explore the Helvetic job offering during December 2020.

The web app can be found [here](https://swiss-job-map.herokuapp.com/). Please visit it and interact ! (You might experience a pretty large loading time : the server as the quit sleeping mode). 

## Scrapping :
First, LinkedIn was scrapped every 3h (thanks to a Raspberry Pi) to make sure that none job ad was missed. Job description and meta data was then collected, processed and stored in a more effective format (panda.DataFrame). The key information are : title, job function (or category), location and publishing date.

## Visualizations and charts :
The ultimate goal is to have a geographical overview of the Swiss job distribution over cities, cantons and functions. Hence, the first element is a map with highlighted cantons’ borders and accessible city coordinates. Then, a pie chart would represent the proportion of job functions and two bar charts would depict the most area (city and canton) that offer the most jobs (overall and per function).

## Web App :
The web app is implemented in Python with the Dash library. Coupled with Plotly plots, the app is highly interactive offering a statistical description of the Swiss employment market under different perspective.

## Conclusion
The project was design to answer questions like :
 * What part of Switzerland hires the most ? 
 * Where could I expect to find companies specialised in biotechnology ? 
 * What kind of jobs are proposed in the canton of Bern ?
 * Does Geneva offers non-profit organizations jobs ?
 
 In few clicks, you might be able to get a description of where certain jobs are more likely to be proposed.
 
 
PS: futur extensions : access the jobs that are stil/currently proposed for each city, develop a temporal analysis, analyse the job description (descriptive NLP)
