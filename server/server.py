from flask import Flask, jsonify, make_response, send_from_directory
import os
from os.path import exists, join
import requests
import pandas as pd
import json
import pyodbc
import datetime
#Azure SQL credentials
server = 'weatherornot-twitter.database.windows.net'
database = 'WON-twitter'
username = 'jonathan'
password = 'Alicehu!1'
driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)


from constants import CONSTANTS
from sample_data import sample_data

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

# Grid Page Endpoint (Jon has no fucking clue, but William does have a clue)
@app.route(CONSTANTS['ENDPOINT']['GRID'])
def get_grid():
    return jsonify(sample_data['text_assets'])

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
        # dictionary and list set up
        # dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
        # list_ = []
        # class instantiation for SQL and deletion
        
        
        query = {'q': x,
            'result_type': 'mixed',
            'count': '100',
            'lang': 'en',
            #'place': 'us',
            'geo-code': '43.414315, -107.054662, 700mi'
            } 

        for status in python_tweets.search(**query)['statuses']:
            #puts tweets into azure
            cursor.execute('insert into Tweets values (?, ?, ?, ?, ?)', 
                status['user']['screen_name'],  
                datetime.datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y'), 
                status['text'], 
                status['favorite_count'], 
                status['retweet_count'])
            #puts tweets into dict
            # dict_['user'].append(status['user']['screen_name'])
            # dict_['date'].append(status['created_at'])
            # dict_['text'].append(status['text'])
            # dict_['favorite_count'].append(status['favorite_count'])
            #puts tweets into other dictionary
            # list_.append({
            #     'user': status['user']['screen_name'],
            #     'date': status['created_at'],
            #     'text': status['text'],
            #     'favorite_count': status['favorite_count']
            #})
    cursor.commit()
    #puts dictionary into panda dataframe
    # df = pd.DataFrame(dict_)
    # df.sort_values(by='favorite_count', inplace=True, ascending=False)
    # df.head(5)
    
    # for todo_item in resp.json():
    #     print('{} {}'.format(todo_item['userId'], todo_item['title']))
    return "test"

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
