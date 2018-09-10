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


class Location(object):

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
  with open('www/locations.json', 'r') as output:
    locs = json.loads(output.read(), encoding='utf8')['locations']
    print 'locations loaded'
    return [
        Location(loc['name'].encode('utf-8').strip(),
                 loc['address'].encode('utf-8').strip()) for loc in locs
    ]


def loadorigin():
  with open('www/locations.json', 'r') as output:
    loc = json.loads(output.read(), encoding='utf8')['origin']
    return {
        "name": loc['name'].encode('utf-8').strip(),
        "address": loc['address'].encode('utf-8').strip()
    }


def savesettings():
  with open('www/settings.json', 'w') as inp:
    inp.write(json.dumps(SETTINGS))
    print 'settings saved'


def startwebserver():
  handler = SimpleHTTPServer.SimpleHTTPRequestHandler
  httpd = SocketServer.TCPServer(("", 80), handler)
  print 'serving at port 80'
  httpd.serve_forever()


def isonduty():
  now = datetime.now().time()
  if ON_TIME <= OFF_TIME:
    return ON_TIME <= now < OFF_TIME
  else:
    return ON_TIME <= now or now < OFF_TIME


def run():
  while True:
    if not isonduty():
      print "out of working hours"
    else:
      try:
        pagesize = 25  # max size for free developer account
        origins = [SETTINGS['origin']['address']]
        alldestinations = [dest.address for dest in LOCATIONS]
        pageddestinations = [
            alldestinations[i:i + pagesize]
            for i in range(0, len(alldestinations), pagesize)
        ]

        for page, destinations in enumerate(pageddestinations):
          ret = GMAPS.distance_matrix(
              origins,
              destinations,
              mode=SETTINGS['params']['mode'],
              language=SETTINGS['params']['language'],
              units=SETTINGS['params']['units'],
              departure_time=datetime.now(),
              traffic_model=SETTINGS['params']['traffic_model'])

          for i, element in enumerate(ret['rows'][0]['elements']):
            locationitem = LOCATIONS[(pagesize * page) + i]

            if element['status'] == 'OK':
              updateelement(element, locationitem)
            else:
              resetelement(locationitem)

          with open('data.json', 'w') as output:
            output.write(json.dumps([obj.__dict__ for obj in LOCATIONS]))

          print 'data.json file updated {0}/{1}\n'.format(
              page + 1, len(pageddestinations))
      except Exception as e:
        print 'Error when getting data from google\n{0}'.format(str(e.message))
        time.sleep(60)

    print 'sleeping for %d min' % UPDATE_INTERVAL
    time.sleep(UPDATE_INTERVAL * 60)


def resetelement(locationitem):
  locationitem.distance = "..."
  locationitem.eta = 0
  locationitem.speed = 0
  locationitem.level = 0
  print '{0} couldn''t updated'.format(locationitem.name)


def updateelement(element, locationitem):
  distance_km = float(element['distance']['value']) / 1000
  duration_hr = float(element['duration_in_traffic']['value']) / 3600

  locationitem.distance = element['distance']['text']
  locationitem.eta = element['duration_in_traffic']['value']
  locationitem.speed = int(round(distance_km / duration_hr, 0))
  locationitem.level = findlevel(locationitem.speed,
                                 int(element['distance']['value']))
  print '{0} updated {1} km - {2} km/h'.format(locationitem.name, distance_km,
                                               locationitem.speed)


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

GMAPS = googlemaps.Client(key=os.environ['api_key'])

LOCATIONS = loadlocations()
SETTINGS = {
    "origin": loadorigin(),
    "params": {
        "mode": os.environ['mode'],
        "language": os.environ['language'],
        "units": os.environ['units'],
        "traffic_model": os.environ['traffic_model'],
        "onhour": os.environ['onhour'],
        "onmin": os.environ['onmin'],
        "offhour": os.environ['offhour'],
        "offmin": os.environ['offmin'],
        "update_interval": os.environ["update_interval"]
    }
}

savesettings()

ON_TIME = time2(
    int(SETTINGS['params']['onhour']), int(SETTINGS['params']['onmin']))
OFF_TIME = time2(
    int(SETTINGS['params']['offhour']), int(SETTINGS['params']['offmin']))

UPDATE_INTERVAL = int(SETTINGS['params']['update_interval'])

print 'working hours is between {0} -> {1}'.format(ON_TIME, OFF_TIME)
print '{0} locations are loaded'.format(len(LOCATIONS))
print 'starting server and updater'

os.chdir('www')

startupdate()
startwebserver()
