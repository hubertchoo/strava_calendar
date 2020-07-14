import gzip
import json
import os
import re
import zipfile

import datetime

from fitparse import FitFile
import tqdm

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
if not os.path.isdir(CACHE):
    os.mkdir(CACHE)


class StravaFile(FitFile):
    def __init__(self, file):
        #super().__init__(file)
        self.data = file.decode()
        self.session_data ={}
        self._get_session_data()
        
        
    def _get_session_data(self):
        #session_data = list(self.get_messages("session"))
        #if len(session_data) != 1:
        #    raise AssertionError("Expected only 1 session record per file!")
        data_list = self.data.split("\n")
        
        #delete all preceding junk before metadata tag
        metadata_reached = False
        while not metadata_reached:
            if "metadata" in data_list[0]:
                metadata_reached = True
            else:
                del data_list[0]

        #set start position as first instance of lat and lon
        start_data_filled = False
        curr_index = 0
        while not start_data_filled:
            if "lat" in data_list[curr_index]:
                start_data_filled = True
                lat_lon_data = data_list[curr_index][:].split('"')
                self.session_data["start_position_lat"] = float(lat_lon_data[1])
                self.session_data["start_position_long"] = float(lat_lon_data[3])
            else:
                curr_index +=1

        #set start time as first instance of time
        start_time_filled = False
        curr_index = 0
        while not start_time_filled:
            if "time" in data_list[curr_index]:
                start_time_filled = True
                time_data = data_list[curr_index][:].split('-')
                year = int(time_data[0][-4:])
                month = int(time_data[1])
                day = int(time_data[2][:2])
                self.session_data["start_time"] = datetime.datetime(year, month, day)
            else:
                curr_index +=1
                
        

        self.session_data["total_distance"] = 0
        self.session_data["total_timer_time"] = 0
        self.session_data["sport"] = "running"
        self.session_data["sub_sport"] = ""
 
        self.data = data_list
        
    def location(self):
        lat, long = (
            self.session_data["start_position_lat"],
            self.session_data["start_position_long"],
        )
        if (lat is not None) and (long is not None):
            lat *= 180.0 / 2 ** 31
            long *= 180.0 / 2 ** 31
        return {"lat": lat, "long": long}

    def route(self):

        coords = []
        for curr_index in range(len(self.data)):
            temp_coord = []
            if "lat" in self.data[curr_index]:
                lat_lon_data = self.data[curr_index][:].split('"')
                temp_coord = [float(lat_lon_data[1]), float(lat_lon_data[3])][::-1]
                coords.append(temp_coord)
        if len(coords) > 0:
            lat, long = zip(*coords)
        else:
            lat, long = [], []
        return {"lat": lat, "long": long}

    def to_json(self):
        return {
            "distance": self.session_data["total_distance"],
            "elapsed_time": self.session_data["total_timer_time"],
            "start_time": self.session_data["start_time"].isoformat(),
            "sport": self.session_data["sport"],
            "sub_sport": self.session_data["sub_sport"],
            "location": self.location(),
            "route": self.route(),
        }


def is_sport(sport="running"):
    def filter_func(strava_file):
        return strava_file.session_data["sport"] == sport

    return filter_func


def is_after(start_date):
    def filter_func(strava_file):
        return strava_file.session_data["start_time"] >= start_date

    return filter_func


def is_before(end_date):
    def filter_func(strava_file):
        return strava_file.session_data["start_time"] < end_date

    return filter_func


def get_files(zip_path):
    #pattern = re.compile(r"^activities/\d+.fit.gz$")
    pattern = re.compile(r"^activities/\d+.gpx$")
    with zipfile.ZipFile(zip_path) as run_zip:
        good_files = [f for f in run_zip.namelist() if pattern.match(f)]
        for filename in tqdm.tqdm(good_files):
            with run_zip.open(filename) as buff:
                #yield gzip.decompress(buff.read())
                yield buff.read()

def filter_files(zip_path, filters):
    for data in get_files(zip_path):
        strava_file = StravaFile(data)
        if all(f(strava_file) for f in filters):
            yield strava_file


def get_data(zip_path, sport, start_date, end_date):
    date_fmt = "%Y-%m-%d"
    zip_fname = os.path.basename(zip_path)
    filter_dir = os.path.join(CACHE, zip_fname)
    if not os.path.isdir(filter_dir):
        os.mkdir(filter_dir)
    filename = os.path.join(
        filter_dir,
        f"{sport}_{start_date.strftime(date_fmt)}_{end_date.strftime(date_fmt)}.json",
    )
    if not os.path.exists(filename):
        filters = [is_sport(sport), is_after(start_date), is_before(end_date)]
        data = {"activities": []}
        for strava_file in filter_files(zip_path, filters):
            data["activities"].append(strava_file.to_json())
        with open(filename, "w") as buff:
            json.dump(data, buff)
    with open(filename, "r") as buff:
        return json.load(buff)

