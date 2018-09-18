#!/usr/bin/env python

import math
import logging


class Location(object):

  def __init__(self, name, address):
    self.reset()
    self.name = name
    self.address = address
    self.distance = "..."
    self.eta = 0
    self.level = 0
    self.speed = 0

  def reset(self):
    self.distance = "..."
    self.eta = 0
    self.speed = 0
    self.level = 0


  def update(self, element):
    distance_km = float(element['distance']['value']) / 1000
    duration_hr = float(element['duration_in_traffic']['value']) / 3600

    self.distance = element['distance']['text']
    self.eta = element['duration_in_traffic']['value']
    self.speed = int(round(distance_km / duration_hr, 0))
    self.level = self.__findlevel(self.speed, int(element['distance']['value']))
    logging.info('%s updated %s km - %s km/h', self.name, distance_km,
                 self.speed)

  @staticmethod
  def __findlevel(speed, distance):
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
