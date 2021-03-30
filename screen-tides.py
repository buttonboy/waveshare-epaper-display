import json
import requests
import datetime
import codecs
import os.path
import time
import sys
import os
import pytz
import logging
#from astral import LocationInfo
#from astral.sun import sun

from utility import is_stale, update_svg

logging.basicConfig(level=logging.DEBUG)

def get_formatted_tides(tides):
    formatted_tides={}
    tide_count = len(tides)
    for i in range(tide_count):
        tide_id = str(i + 1)
        if (i <= tide_count):
            formatted_tides['TIDE_TIME_' + tide_id] = get_datetime_formatted(tides[i]['t'])
            formatted_tides['TIDE_TYPE_' + tide_id] = tides[i]['type']
            formatted_tides['TIDE_HEIGHT_' + tide_id] = tides[i]['v']
        else:
            formatted_tides['TIDE_TIME_' + tide_id] = ""
            formatted_tides['TIDE_TYPE_' + tide_id] = ""
            formatted_tides['TIDE_HEIGHT_' + tide_id] = ""
    return formatted_tides

def get_datetime_formatted(input_time):
    #time = input_time.strftime("%-I:%M %p")
    dt_obj = datetime.datetime.strptime(input_time, '%Y-%m-%d %H:%M')
    time = dt_obj.strftime("%I:%M%p %m/%d")
    return time

def get_tides():
    dt = datetime.datetime.now()
    today = dt.strftime("%Y%m%d")

    logging.info("{}, {}".format(dt,today))
    
    url = ("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions" + 
    "&begin_date={}&end_date={}&datum=MLLW&station=8632837&time_zone=lst_ldt&units=english&interval=hilo&format=json"
    .format(today,today))

    filepath = os.getcwd() + "/" + "noaa-tides.json"
    ttl = float(os.getenv("WEATHER_TTL", 1 * 60 * 60))
    try:
        response_data = get_response_data(url, filepath, ttl)
        tides = response_data
        #tides = response_data['timelines'][0]['intervals'][0]['values']
        logging.info("get_tides() - {}".format(tides))
        logging.info("{}".format(url))
    except Exception as error:
        logging.error(error)
        tides = False

    return tides

def get_response_data(url, filepath, ttl):

    response_json = False

    if (is_stale(filepath, ttl)):
        try:
            response_data = requests.get(url).text
            response_json = json.loads(response_data)['predictions']
            with open(filepath, 'w') as text_file:
                text_file.write(response_data)
        except Exception as error:
            logging.error(error)
            raise
    else:
        with open(filepath, 'r') as file:
            return json.loads(file.read())['predictions']
    return response_json

def main():
    #url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&date=today&datum=MLLW&station=8632837&time_zone=lst_ldt&units=english&interval=hilo&format=json&application=NOS.COOPS.TAC.TidePred"
    


    #response = get_response_data(url,filepath,ttl)
    #logging.info("{}".format(response))
    tides = get_tides()

    if (tides == False):
        logging.error("Unable to fetch Tide Information. SVG will not be updated.")
        return
    
    tide_output = get_formatted_tides(tides)
    logging.info("{}".format(tide_output))

    output_svg_filename = 'screen-output-weather.svg'
    update_svg(output_svg_filename, output_svg_filename, tide_output)

if __name__ == "__main__":
    main()