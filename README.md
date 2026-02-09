# Overview

I have built a "News Wordle" Python app that has players identify subjects within the day's top 5 headlines using a hint-based guessing system. 

## About the API

It uses the NewsAPI to fetch real-time global news data.

How the API is called:
It uses the requests module to send a web query and parse the response.
The API returns the data in JSON format, and this is converted into a dictionary containing a list of articles. 

Key parameters:
- apiKey
- country: set to US to retrive headlines specific to the United States