# coding: utf-8
"""Server side Tweet_Analytics."""
from flask import Flask, Response, request
from flask import render_template
from pymongo import MongoClient
import json
from bson import json_util
import pandas
import random

app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'twitter_analytics'
COLLECTION_NAME = 'tweets_sentiment'
FIELDS = {'State': True, 'SentimentText': True,
          'Timestamp': True, 'Sentiment': True, '_id': False}


@app.route("/")
def index():
    """Return the index page."""
    return render_template("index.html")


@app.route("/tweets/analytics", methods=['GET'])
def tweet_analytics():

    hachtag = request.values.get("hachtag", None)
    if (hachtag == 'undefined') or (hachtag == 'all') or (hachtag is None):
        hachtag = None
    else:
        hachtag = str(hachtag).split(',')
    """Connection to mongoDB."""
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS, limit=10000)
    # projects = collection.find(projection=FIELDS)
    json_projects = []

    for project in projects:
        if(hachtag is not None):
            ishachtag = False
            tweet = project['SentimentText']
            for word in tweet.split():
                if any(word == s for s in hachtag):
                    print project
                    ishachtag = True
            if not ishachtag:
                continue
        # if hachtag in project['SentimentText']:
        json_projects.append(project)

    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects


@app.route('/word_count', methods=['GET'])
def get_word_count():
    state = request.values.get("state", None)
    sentiment = request.values.get("sentiment", None)

    if (state == 'undefined') or (state == 'all') or (state is None):
        state = None
    else:
        state = str(state).split(',')
    # print 'state', state

    # print 'sentiment', sentiment
    if (sentiment == 'undefined') or (sentiment == 'all') or (sentiment is None):
        sentiment = None
    else:
        sentiment = str(sentiment).split(',')
        if len(sentiment) == 2:
            sentiment = None
        elif 'Positive' in sentiment:
            sentiment = 0
        elif 'Negative' in sentiment:
            sentiment = 1
    # get tweets from the queue
    tweets = tweet_analytics()
    # dont count these words
    ignore_words = ["rt", "chelsea"]
    words = []
    tweets = json.loads(tweets)
    # print loc
    for tweet in tweets:
        if state is not None:
            try:
                if tweet['State'] not in state:
                    continue
            except:
                continue
        
        if sentiment is not None:
            try:
                if sentiment is not tweet['Sentiment']:
                    continue
            except:
                continue
        print tweet

        tweet = tweet['SentimentText']

        for word in tweet.split():
            word = word.replace(',', '').replace(';', '')
            if (word not in ignore_words) and ('#' in word):
                words.append(word)

    p = pandas.Series(words)
    # get the counts per word
    freq = p.value_counts()
    freq = freq.ix[0:40]
    # how many max words do we want to give back
    response = Response(freq.to_json())
    # response = json.dumps(freq)
    response.headers.add('Access-Control-Allow-Origin', "*")
    return response


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
