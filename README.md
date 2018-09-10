# Google Traffic Screen [![Build Status](https://travis-ci.org/alatas/google-traffic-screen.svg?branch=master)](https://travis-ci.org/alatas/google-traffic-screen)
It's a project that can display the latest traffic information based on an origin location to multiple different locations. It uses Google Distance Matrix API. You need a valid GoogleMaps API key to query the latest information.

Now, It's only available as docker image only

## Quick Start
```
docker pull alatas/google-traffic-display
docker run -ti -p 80:80 -e "api_key=your google maps api key" alatas/google-traffic-display
```
