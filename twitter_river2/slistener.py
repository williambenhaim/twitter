"""Class to deal with Tweets."""
from tweepy import StreamListener
import json
import time
import sys
import pandas as pd
import pickle
from mechanize import Browser
from urllib2 import urlopen
from time import sleep


class SListener(StreamListener):
    """Class SListener to deal with Twitter's status."""

    def __init__(self, api=None, fprefix='streamer'):
        """Init methode to initialize variables."""
        self.api = api
        self.counter = 0
        self.fprefix = fprefix
        self.df_tweet = pd.DataFrame(columns=['Text', 'Longitude', 'Latitude', 'State', 'Timestamp'])
        self.delout = open('delete.txt', 'a')
        self.dict_location = self.load_dict("dict_location_tweet")
        self.error = 0
        self.br = Browser()

    def on_data(self, data):
        """Deal on data (tweepy method)."""
        if 'in_reply_to_status' in data:
            self.on_status(json.loads(data))

    def on_status(self, status):
        """Deal on tweet (tweepy method)."""
        if status["lang"] == "en":
            if status["text"] is not None:

                if status['user'] is not None:
                    if status["user"]["location"] is not None:
                        loc_tweet = self.print_time(self.br, status["user"]["location"])
                        self.df_tweet.loc[self.df_tweet.shape[0]] = [status["text"].encode('utf8'), loc_tweet["Longitude"], loc_tweet["Latitude"], loc_tweet["State"], status["timestamp_ms"]]
                    else:
                        self.df_tweet.loc[self.df_tweet.shape[0]] = [status["text"].encode('utf8'), 0.0, 0.0, '', status["timestamp_ms"]]

        print self.df_tweet

        self.counter += 1
        if self.df_tweet.shape[0] % 100 == 0:
            print self.counter
            self.df_tweet.to_csv('tweet_info_new.csv', sep='\t', index=False)
            self.save_dict(self.dict_location, 'dict_location_tweet')
        return

    def on_delete(self, status_id, user_id):
        """Method to delete tweet based on the @status_id and @user_id."""
        self.delout.write(str(status_id) + "\n")
        return

    def on_limit(self, track):
        """Limit tweet based on the @track."""
        sys.stderr.write(track + "\n")
        return

    def on_error(self, status_code):
        """Error on tweet based on the @status_code."""
        sys.stderr.write('Error: ' + str(status_code) + "\n")
        sleep(10)
        return False

    def on_timeout(self):
        """Timeout method."""
        sys.stderr.write("Timeout, sleeping for 60 seconds...\n")
        time.sleep(60)
        return

    def save_dict(self, obj, name):
        """Save obj pickle."""
        with open(name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_dict(self, name):
        """Load obj pickle."""
        try:
            with open(name + '.pkl', 'rb') as f:
                return pickle.load(f)
        except (OSError, IOError):
            self.dict_location = {}
            self.save_dict(self.dict_location, 'dict_location_tweet')

    def geocode(self, address):
        """Get the State of address."""
        url = ("http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address={0}".format(address.replace(" ", "+")))
        return json.loads(urlopen(url).read())

    def print_time(self, br, location):
        """Method to get the location of a tweet."""
        longitude = 0.0
        latitude = 0.0
        state = ''
        # print location
        if location not in self.dict_location.keys():
            try:
                self.dict_location[location] = {}
                json_loc = self.geocode(location)
                if len(json_loc["results"]) > 0:
                    for j in json_loc["results"][0]["address_components"]:
                        if "administrative_area_level_1" in j["types"]:
                            state = j["short_name"]

                    latitude = json_loc["results"][0]["geometry"]["location"]["lat"]
                    longitude = json_loc["results"][0]["geometry"]["location"]["lng"]

                    # print str(longitude) + " -- " + str(latitude) + " -- " + state

                self.dict_location[location]["Longitude"] = longitude
                self.dict_location[location]["Latitude"] = latitude
                self.dict_location[location]["State"] = state

            except Exception as inst:
                print(type(inst))    # the exception instance
                print(inst)
                self.dict_location[location]["Longitude"] = longitude
                self.dict_location[location]["Latitude"] = latitude
                self.dict_location[location]["State"] = state

        return self.dict_location[location]
