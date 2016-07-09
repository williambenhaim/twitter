from urllib2 import urlopen
import csv
import json
from time import sleep

def geocode(address):
    url = ("http://maps.googleapis.com/maps/api/geocode/json?"
        "sensor=false&address={0}".format(address.replace(" ", "+")))
    return json.loads(urlopen(url).read())

for i in range(1):
    print geocode("new york").keys()
    for j in geocode("new york")["results"][0]["address_components"]:
        if "administrative_area_level_1" in j["types"]:
            state = j["short_name"]
            print state
    print geocode("new york")["results"][0]["geometry"]["location"]["lat"]
    print geocode("new york")["results"][0]["geometry"]["location"]["lng"]
    sleep(0.2)

print "Done writing file"