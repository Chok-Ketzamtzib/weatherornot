from flask import Flask, jsonify, make_response, send_from_directory, render_template
import os
from os.path import exists, join
import requests
import pandas as pd
import json
import pyodbc
import datetime
import itertools


#Azure SQL credentials
server = 'weatherornot-twitter.database.windows.net'
database = 'WON-twitter'
username = 'jonathan'
password = 'Alicehu!1'
driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)


from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials

subscription_key = '6dd24538cfe444bb8a9cd7d4f21e31be'
endpoint = 'https://weatherornottextanalytics.cognitiveservices.azure.com/'

from twython import Twython
#twitter credentials
credentials = {}
credentials['CONSUMER_KEY'] = 'gydnfRqYpRi2c3AzEOtP9Kx9P'
credentials['CONSUMER_SECRET'] = 'qxOTin47djJzMi7Ksl4ZGM159tvrSq9QnKnpjRvqkNiEUb45CF'
credentials['ACCESS_TOKEN'] = '776289912706314240-DsxvumZ0KJPWGulUr51PxzoXdQvE46S'
credentials['ACCESS_SECRET'] = '95ilPQV1yeoHiUdVSSCwUtPVe8G6UhZrm0wyqSUaYoldC'
#twitter credential stored into json file
with open("twitter_credentials.json", "w") as file:
    json.dump(credentials, file)
Disasters = ['tornado', 'drought', 'hurricane', 'wildfire', 'heatwave',
'thunderstorm','cylone','blizzard', 'storm', 'flood', 'earthquake',
'thoughts and prayers', 'thoughts go out','prayers go out', 'weather',
'natural disaster','heavy downpours']

app = Flask(__name__, static_folder='build')

# Grid Page Endpoint (Jon has no  clue, but William does have a clue)
# @app.route(CONSTANTS['ENDPOINT']['GRID'])
# def get_grid():
#     return jsonify(sample_data['text_assets'])

@app.route('/', methods=['GET'])
def default():
    print('Hello')
    return render_template('index.html', src=["https://www.youtube.com/embed/TImO_RquoW8?controls=0",
     "https://www.youtube.com/embed/TImO_RquoW8?controls=0", "https://www.youtube.com/embed/TImO_RquoW8?controls=0",
      "https://www.youtube.com/embed/TImO_RquoW8?controls=0", "https://www.youtube.com/embed/TImO_RquoW8?controls=0",
       "https://www.youtube.com/embed/TImO_RquoW8?controls=0"], title=['a', 'b', 'c', 'd', 'e', 'f'])

# @app.route('/insertSearchResults')
# def insertSearchResults():
   
#     googleLinks =  requests.data.links
#     cursor = cnxn.cursor()
#     cursor.execute('insert into googleLinks values (?)', '')


#test, but also calls the twitter api, stores result from query into Azure
@app.route('/test')
def test():
    #opens up twitter cred json
    with open("twitter_credentials.json", "r") as file:
        creds = json.load(file)
    #twitter search api
    python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    
    cursor = cnxn.cursor()
    cursor.execute('delete from Tweets')

    for x in Disasters:        
        
        query = {'q': x,
            'result_type': 'mixed',
            'count': '100',
            'lang': 'en',
            #'place': 'us',
            'geo-code': '43.414315, -107.054662, 700mi'
            } 

        for status in python_tweets.search(**query)['statuses']:
            #puts tweets into azure
            cursor.execute('insert into Tweets values (?, ?, ?, ?, ?, ?)', 
                status['user']['screen_name'],  
                datetime.datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y'), 
                status['text'], 
                status['retweet_count'], '','')
    cursor.commit()
    return "test"

def authenticateClient():
    credentials = CognitiveServicesCredentials(subscription_key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credentials=credentials)
    return text_analytics_client

@app.route('/cluster')
def cluster():
    client = authenticateClient()
    result = ''    
    
    #use cursor
    cursor = cnxn.cursor()
    cursor.execute('SELECT TOP 10 * FROM Tweets') #!!! 1500
    columns = [column[0] for column in cursor.description]
    twts = []

    for row in cursor.fetchall():
        twts.append(dict(zip(columns, row)))
    cursor.commit()
    print(twts)

    try:
        response = client.entities(documents=twts)

        for document in response.documents:
            result.append("Text: ", document.text)
            print("\tKey Entities:")
            for entity in document.entities:
                print("\t\t", "NAME: ", entity.name, "\tType: ",
                      entity.type, "\tSub-type: ", entity.sub_type)
                for match in entity.matches:
                    print("\t\t\tOffset: ", match.offset, "\tLength: ", match.length, "\tScore: ",
                          "{:.2f}".format(match.entity_type_score))

    except Exception as err:
        print("Encountered exception. {}".format(err))
    entity_recognition()
    return result
           

# Catching all routes
# This route is used to serve all the routes in the frontend application after deployment.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    file_to_serve = path if path and exists(join(app.static_folder, path)) else 'index.html'
    return send_from_directory(app.static_folder, file_to_serve)

# Error Handler
@app.errorhandler(404)
def page_not_found(error):
    json_response = jsonify({'error': 'Page not found'})
    return make_response(json_response, CONSTANTS['HTTP_STATUS']['404_NOT_FOUND'])

if __name__ == '__main__':
    app.run(port=5000)
