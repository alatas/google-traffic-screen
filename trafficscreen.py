#!/usr/bin/env python

import json
import os
import SimpleHTTPServer
import SocketServer
import threading
import time
import logging
import sys
from datetime import datetime
from datetime import time as time2

from location import Location

import googlemaps
import yaml

def savelocations():
  with open('data.json', 'w') as output:
    output.write(json.dumps([obj.__dict__ for obj in LOCATIONS]))


def loadlocations():
  with open('locations.yml', 'r') as output:
    locs = yaml.safe_load(output)['locations']
    logging.info('%d locations loaded', len(locs))
    return [
        Location(loc['name'].encode('utf-8').strip(),
                 loc['address'].encode('utf-8').strip()) for loc in locs
    ]


def savesettings():
  with open('www/settings.json', 'w') as inp:
    inp.write(json.dumps(SETTINGS))
    logging.info('settings saved')


def loadsettings():
  with open("settings.yml", 'r') as stream:
    logging.info('settings loaded')
    return yaml.safe_load(stream)


def startwebserver():
  handler = SimpleHTTPServer.SimpleHTTPRequestHandler
  httpd = SocketServer.TCPServer(("", 80), handler)
  logging.info('serving at port 80')
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
      logging.debug("out of working hours")
    else:
      try:
        pagesize = 25
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
              mode=SETTINGS['api_params']['mode'],
              language=SETTINGS['api_params']['language'],
              units=SETTINGS['api_params']['units'],
              departure_time=datetime.now(),
              traffic_model=SETTINGS['api_params']['traffic_model'])

          for i, element in enumerate(ret['rows'][0]['elements']):
            locationitem = LOCATIONS[(pagesize * page) + i]

            if element['status'] == 'OK':
              locationitem.update(element)
            else:
              logging.info('%s couldn' 't updated', locationitem.name)
              locationitem.reset()

          savelocations()

          logging.info('data.json file updated %d/%d', page + 1,
                       len(pageddestinations))
      except Exception as e:
        logging.error('Error when getting data: %s', str(e.message))
        time.sleep(60)

    logging.info('sleeping for %d min', UPDATE_INTERVAL)
    time.sleep(UPDATE_INTERVAL * 60)


def startupdate():
  thread = threading.Thread(target=run)
  thread.daemon = True
  thread.start()


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s')

LOCATIONS = loadlocations()
SETTINGS = loadsettings()
GMAPS = googlemaps.Client(key=SETTINGS['api_params']['api_key'])
SETTINGS['api_params']['api_key'] = ""
savesettings()

ON_TIME = time2(
    int(SETTINGS['schedule']['onhour']), int(SETTINGS['schedule']['onmin']))
OFF_TIME = time2(
    int(SETTINGS['schedule']['offhour']), int(SETTINGS['schedule']['offmin']))

UPDATE_INTERVAL = int(SETTINGS['schedule']['update_interval'])

logging.info('working hours is between %s -> %s', ON_TIME, OFF_TIME)
logging.info('%d locations are loaded', len(LOCATIONS))
logging.info('starting server and updater')

os.chdir('www')

startupdate()
startwebserver()
