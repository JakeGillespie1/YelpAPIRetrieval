#Import Needed Packages -- This was developed in Google Colab, Credit Jake Gillespie
import requests as r, json, pandas as pd, time
from datetime import datetime
from posixpath import join

#Call the API
key = 'Your API Authorization Key Goes Here'

#Get the headers set up
headers = {'Authorization':('Bearer '+ key), 'accept':'application/json'}

#Resturaunt alias search using various locations (Enter Your Favorite Cities and How many resturaunts you want to see per city)
#Here, there may be some cities (i.e. NYC that are finnicky because of the three letter name. Those bugs are being worked on (NYC is fixed))
cities = ['City1', 'City2']
limit = 0

#Setup lists
business_aliases = []
ratings = []

#This loop will grab places to eat in the locations list
for city in cities:
  url1 = f'https://api.yelp.com/v3/businesses/search?sort_by=best_match&limit={limit}&location={city}'
  response = r.get(url=url1, headers=headers)
  json_data = json.loads(response.text)
  json_formatted = json.dumps(json_data, indent=2)
  for iCount in range(0,limit):
    business_aliases.append(json_data['businesses'][iCount]['alias'])
    ratings.append(json_data['businesses'][iCount]['rating'])

#Get the businesses and number of reviews you want to see ready
urls = []
#Create the DataFrame
df = pd.DataFrame(columns=['rating', 'name', 'text', 'id'])

#Loop to display the json text
for business in business_aliases:
  urls.append(f'https://api.yelp.com/v3/businesses/{business}/reviews?sort_by=newest')

#Weekdays dictionary for day of week that the review was left & URL parsing setup (to get alias)
weekdays = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
url_search_keys = ['businesses/', '/reviews']
cityCount = 0
aliases = []

#Call the 3 newest reviews per resturaunt found and load them into the dataframe
for url in urls:
  response = r.get(url=url, headers=headers)
  json_data = json.loads(response.text)
  json_formatted = json.dumps(json_data, indent=2)
  #get the unparsed alias inside of an array to clean up in a later array
  business = url[(url.index(url_search_keys[0]) + len(url_search_keys[0])):(url.index(url_search_keys[1]))]
  aliases.append(business)
  for iCount in range(0,3):
    #Day of week Processing
    date_time = (json_data['reviews'][iCount]['time_created'])
    date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    week_day = date_time.weekday()
    #Add a new row to the data frame with the needed data
    new_row = pd.DataFrame({'rating':[json_data['reviews'][iCount]['rating']], 'name':[json_data['reviews'][iCount]['user']['name']], 'day_of_week':[weekdays[week_day]] ,'text':[json_data['reviews'][iCount]['text']], 'id':[json_data['reviews'][iCount]['user']['id']]})
    df = pd.concat([df, new_row], ignore_index=True)

#Loop to add the city name and other information about the location as needed
cityCount = 0
df['city'] = ''
for iCount in range(0, 3*(len(cities)*limit)):
  #Increment the city name every three reviews
  if iCount%(3*limit) == 0 and iCount > 0:
    cityCount+=1
  #Adds the needed columns one row at a time
  #Special Case for NYC
  if ('New%20York%20City' in cities[cityCount]):
    cities[cityCount] = cities[cityCount].replace('%20City', '')
  df.loc[iCount, 'city'] = cities[cityCount].replace('%20', ' ')

resturauntCount = 0
rowCount = 0
for iCount in range(0, (len(cities)*limit)):
  #Increment the city name every 2 resturaunts
  if iCount%(limit) == 0 and iCount > 0:
    resturauntCount+=1
  #String Parsing and Preparing
  business = (str(aliases[iCount])).split(sep='-')
  if '%20' in cities[resturauntCount]:
    cities[resturauntCount] = cities[resturauntCount].replace('%20', ' ')
    lastSpace = cities[resturauntCount].rfind(" ")
    cities[resturauntCount] = cities[resturauntCount][lastSpace + 1:]
  business =  business[0:business.index(cities[resturauntCount].lower())+1]
  business = ' '.join(business).title()
  for iInnerCount in range(0,3):
    df.loc[rowCount, 'business_alias'] = business
    df.loc[rowCount, 'overall_resturaunt_rating'] = ratings[iCount]
    rowCount+=1

#Finally, set the index to houston to group all the items
df.set_index('business_alias', inplace=True)

#Save df to a csv
path = 'Google/Drive/Path.csv'
#mode a = append the data. headers false = dont add new headers as you append
df.to_csv(f'{path}/Yelp.csv', mode='a', header=True)
df
