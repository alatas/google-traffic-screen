#!/usr/bin/env python

import json
import math
import os
import SimpleHTTPServer
import SocketServer
import threading
import time
from datetime import datetime
from datetime import time as time2
from shutil import copyfile

import googlemaps


class Location:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.distance = "",
        self.eta = "",
        self.level = 0,
        self.speed = 0


def copydefaults():
    if not os.path.isfile('www/index.html'):
        print 'default index file copied'
        copyfile('www/default-index.html', 'www/index.html')

    if not os.path.isfile('www/locations.json'):
        print 'default locations copied'
        copyfile('www/default-locations.json', 'www/locations.json')


def loadlocations():
    with open('locations.json', 'r') as output:
        print 'locations loaded'
        return json.loads(output.read(), encoding='utf8')


def savesettings():
    with open('settings.json', 'w') as input:
        input.write(json.dumps(settings))
        print 'settings saved'


def startwebserver():
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", 80), Handler)
    print 'serving at port 80'
    httpd.serve_forever()


def isonduty():
    now = datetime.now().time()
    if ontime <= offtime:
        return ontime <= now < offtime
    else:
        return ontime <= now or now < offtime


def run():
    while True:
        if not isonduty():
            print "out of working hours"
        else:
            try:
                pagesize = 25  # max size for free developer account
                origins = [settings['origin']['address']]
                alldestinations = [dest.address for dest in locations]
                pageddestinations = [alldestinations[i:i+pagesize]
                                     for i in range(0, len(alldestinations), pagesize)]

                for page, destinations in enumerate(pageddestinations):
                    ret = gmaps.distance_matrix(origins, destinations, mode=settings['params']['mode'], language=settings['params']['language'],
                                                units=settings['params']['units'], departure_time=datetime.now(), traffic_model=settings['params']['traffic_model'])

                    for i, element in enumerate(ret['rows'][0]['elements']):
                        locationItem = locations[(pagesize * page) + i]

                        if element['status'] == 'OK':
                            updateelement(element, locationItem)
                        else:
                            resetelement(locationItem)

                    with open('data.json', 'w') as output:
                        output.write(json.dumps(
                            [obj.__dict__ for obj in locations]))

                    print 'data.json file updated {0}/{1}\n'.format(
                        page+1, len(pageddestinations))
            except Exception as e:
                print 'Error when getting data from google\n{0}'.format(str(e))
                time.sleep(60)

        print 'sleeping for 3 min'
        time.sleep(3 * 60)


def resetelement(locationItem):
    locationItem.distance = "..."
    locationItem.eta = 0
    locationItem.speed = 0
    locationItem.level = 0
    print '{0} couldn''t updated'.format(locationItem.name)


def updateelement(element, locationItem):
    distance_km = float(element['distance']['value']) / 1000
    duration_hr = float(element['duration_in_traffic']['value']) / 3600

    locationItem.distance = element['distance']['text']
    locationItem.eta = element['duration_in_traffic']['value']
    locationItem.speed = int(round(distance_km / duration_hr, 0))
    locationItem.level = findlevel(
        locationItem.speed, int(element['distance']['value']))
    print '{0} updated {1} km - {2} km/h'.format(
        locationItem.name, distance_km, locationItem.speed)


def findlevel(speed, distance):
    level1 = 6 * math.log(0.000984982 * distance)
    level2 = 12 * math.log(0.000984982 * distance)
    level3 = 17 * math.log(0.000984982 * distance)
    if speed <= level1:
        return "1"
    elif speed <= level2:
        return "2"
    elif speed <= level3:
        return "3"
    else:
        return "4"


def startupdate():
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()


copydefaults()
os.chdir('www')
gmaps = googlemaps.Client(key=os.environ['api_key'])

locations = loadlocations()
settings = {"origin": locations['origin'], "params": {"mode": os.environ['mode'],
                                                      "language": os.environ['language'],
                                                      "units": os.environ['units'],
                                                      "traffic_model": os.environ['traffic_model'],
                                                      "onhour": os.environ['onhour'],
                                                      "onmin": os.environ['onmin'],
                                                      "offhour": os.environ['offhour'],
                                                      "offmin": os.environ['offmin']}}
savesettings()
locations = [Location(loc['name'].encode('utf-8').strip(), loc['address'].encode('utf-8').strip())
             for loc in locations['locations']]

ontime = time2(int(settings['params']['onhour']),
               int(settings['params']['onmin']))
offtime = time2(int(settings['params']['offhour']),
                int(settings['params']['offmin']))

print 'working hours is between {0} -> {1}'.format(ontime, offtime)
print '{0} locations are loaded'.format(len(locations))
print 'starting server and updater'

startupdate()
startwebserver()
