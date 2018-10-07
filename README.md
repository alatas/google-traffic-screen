# Google Traffic Screen [![Build Status](https://travis-ci.org/alatas/google-traffic-screen.svg?branch=master)](https://travis-ci.org/alatas/google-traffic-screen)
This is one of the side projects that I develop and add new features from time to time. 

Basically, It's a small single page website that can display the latest traffic information based on an origin location to multiple different locations. It uses Google Distance Matrix API to query the latest ETA from Google Maps. You need a valid GoogleMaps API key to query.

![Screenshot](https://i.imgur.com/xVXwlB3.png)

## Quick Start

### With Docker

1. Download the [latest release](https://github.com/alatas/google-traffic-screen/releases/latest) and unzip. You may use the command below or do it manually.

```shell
curl -s https://api.github.com/repos/alatas/google-traffic-screen/releases/latest | grep "browser_download_url.*docker.zip" | head -1 | cut -d : -f 2,3 | cut -d '"' -f 2 | xargs curl -L -o release.zip ; unzip release.zip ; rm release.zip
```

2. Edit settings.yml and fill your google maps api key to the file. (Optional) Edit locations.yml file

3. Download and run the Docker container

```shell
docker-compose up
```

4. Browse http://localhost:8901/

### Without Docker

1. Install the prerequisities (with pip)

```shell
pip install -U googlemaps pyyaml
```

2. Download the [latest release](https://github.com/alatas/google-traffic-screen/releases/latest) and unzip. You may use the command below or do it manually.

```shell
curl -s https://api.github.com/repos/alatas/google-traffic-screen/releases/latest | grep "browser_download_url.*[^docker].zip" | head -1 | cut -d : -f 2,3 | cut -d '"' -f 2 | xargs curl -L -o release.zip ; unzip release.zip ; rm release.zip
```

3. Edit settings.yml and fill your google maps api key to the file. (Optional) Edit locations.yml file

4. Run the script

```shell
python trafficscreen.py
```

5. Browse http://localhost:8901/

## Settings

Google Distance Matrix API has some customization options for calculation ETA value. Additionally, the script has schedule options to consume your API quota efficiently.

| Tag | Example | Description |
| --- | --- | --- |
| origin | | |
| name | Grand Central Terminal | The name of the origin, that shown on the top of the display. |
| address | 89 E 42nd St, New York, NY | The address of the origin. It is a significant information for the calculation.
| | | |
| api_params | | |
| api_key | | You have to create a Google Cloud account and get a Maps API key. ([for more information see below](#google-maps-api-key))
| mode | driving | For the calculation of distances, you may specify the transportation mode. The following travel modes are supported: `driving` indicates distance calculation using the road network. `walking` requests distance calculation for walking via pedestrian paths & sidewalks (where available). `bicycling` requests distance calculation for bicycling via bicycle paths & preferred streets (where available). `transit` requests distance calculation via public transit routes (where available) |
| language | en | The language in which to return results. You refer [Google Maps API Documentation](https://developers.google.com/maps/faq#languagesupport) for the list of available languages |
| units | imperial | Specifies the unit system to use when expressing distance as text. `metric` returns distances in kilometers and meters. `imperial` returns distances in miles and feet |
| traffic_model | best_guess | Specifies the assumptions to use when calculating time in traffic. `best_guess` indicates that the returned ETA should be the best estimate of travel time given what is known about both historical traffic conditions and live traffic. `pessimistic` indicates that the returned ETA should be longer than the actual travel time on most days, though occasional days with particularly bad traffic conditions may exceed this value. `optimistic` indicates that the returned ETA should be shorter than the actual travel time on most days, though occasional days with particularly good traffic conditions may be faster than this value. |
| | | |
| [schedule*](#google-maps-api-usage) | | |
| onhour | 17 | This value indicates the start hour of the on-duty time in 24h format. |
| onmin | 30 | This value indicates the start minute of the on-duty time. |
| offhour | 20 | This value indicates end hour of the on-duty time in 24h format. |
| offmin | 00 | This value indicates the end minute of the on-duty time. |
| update_interval | 6 | The calculation interval in minutes. |
| | | |
| environment | | |
| TZ | UTC | Time zone value of the system. You can use one of the possible time zone values [listed by IANA](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List). |
| all_proxy | http://proxy:8080 | You can use this field to specify a proxy server to access the internet if you need or leave it blank.|

## Theming

This is a single page application that uses Angular (v1.6.5), jquery (v3.2.1) and momentjs (v2.22.2). You may manually edit the `index.html` file in `www` folder to change the default theme. The CSS and JS elements are included in the `index.html` file.

## Google Maps API Key

To use the Distance Matrix API, you must get an API key. The API key is used to track API requests associated with your project for quota, usage, and billing. [According to new rules of Google Cloud](https://developers.google.com/maps/billing/important-updates?__utma=236542612.2044528118.1532158969.1538832276.1538832276.1&__utmb=236542612.0.10.1538832276&__utmc=236542612&__utmx=-&__utmz=236542612.1538832276.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)&__utmv=-&__utmk=268575666&_ga=2.45834659.686116827.1538823952-2044528118.1532158969), you must enable billing to get a Maps API key.

Follow these steps to get an API key and set up restrictions:

1. Go to the [Google Cloud Platform Console](https://cloud.google.com/console/google/maps-apis/overview).
1. Select the project for which you want to add an API key.
1. Go to the **Credentials** page. (From the Navigation menu click **APIs & Services > Credentials**.)
1. Click **Create credentials > API key**. The API key created dialog displays your newly created API key. Copy this key and paste into the appropriate field in settings.yml file. The following steps are optional.
1. Click **Restrict Key**. (If you click Close, you can still set up restrictions later.)
1. On the API key page, under Key restrictions, set the **Application restrictions**.
   * Select **IP addresses**
   * Add the IP addresses that you are using
   * Click **Save**

## Google Maps API Usage

For each billing account, for qualifying Google Maps Platform SKUs, a $200 USD Google Maps Platform credit is available each month. This means that you can use $200 worth Maps APIs for free each month. If you don't want to pay extra, you have to arrange your API usage to this limitation.

[On the current pricing of the API](https://developers.google.com/maps/documentation/distance-matrix/usage-and-billing#distance-matrix-advanced), It's 0.01 USD per each item queried. Your monthly free quota, $200 equals to 20.000 items that should be queried per month for free. You have to arrange schedule settings to keep usage in this limit.

The formula is very simple as follows:

![Formula](https://latex.codecogs.com/gif.latex?%3D%7CDays%7C%5C%2C%20%5Cast%5C%2C%20%7CLocations%7C%5C%2C%20%5Cast%5C%2C%20%5Cfrac%7BWorking%5C%2CDuration%5C%2C%20per%5C%2C%20Day%7D%7BQuery%5C%2C%20Interval%7D)

And also, you can set a quota to API to keep its in limits in Google Cloud Console.

### Example 1 (Default Values)

Default schedule is every day 5:30 PM to 8:00 PM and the default interval is 6 minutes.

There are 2.5 hours (150 minutes) between 5:30PM to 8:00PM, this equals 150min / 6min interval = 25 data query per day.

There are 26 locations in default locations.yml file. That means 26 locations x 25 data query = 650 items are queried per day. 650 x 30 day = 19.500 items queried per month. Default values is barely in the limits.

### Example 2

There are 15 locations to query and the schedule is 8:00 AM to 8:00 PM every day.

We can calculate the maximum interval for keeping the usage in free limits.

![Example2](https://latex.codecogs.com/gif.latex?%5C%5C%20%5C%5C%20interval%20%3D%20%5Cfrac%7B720min%5C%20%5Cast%5C%2015locs%5C%20%5Cast%5C%2030days%7D%7B20.000%7D%20%5C%5C%20%5C%5C%20interval%20%3D%20%5Cfrac%7B324.000%7D%7B20.000%7D%20%5C%5C%20%5C%5C%20interval%20%3D%2016.2)