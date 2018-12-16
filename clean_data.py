#!/usr/bin/env python
"""clean and transform the weather data"""
import argparse
import json
import pathlib
from typing import Any, Dict, List

from utils import load_data


def get_station_with_most_records() -> Dict[str, str]:
    """get a mapping from county to station containing the
    greatest number of records"""
    # get a `Path` to the data directory
    csv_directory = pathlib.Path(args.directory)

    county_station: Dict[str, str] = {}

    with open('data/stations.json', 'rt') as f:
        stations = json.load(f)

    # iterate through all counties
    for county in stations.keys():
        highest_n_years = 0
        # iterate through each weather station inthe county
        for station in stations[county]:
            # construct the filepath
            filepath = csv_directory / station['filename']

            # load the DataFrame
            df = load_data(filepath, station=station)

            try:
                start = df.iloc[0].year
            except IndexError:
                continue
            try:
                end = df.iloc[-1].year
            except IndexError:
                continue

            # keep track of the number of years recorded for
            # the current station, and keep track of the
            # station with the highest number of records
            # available
            n_years = end-start
            if n_years > highest_n_years:
                highest_n_years = n_years
                station_most_years = station['station']

        county_station[county] = station_most_years

    # don't want this record
    del county_station['Buoys']

    return county_station


def rainfall_year_month_by_county(county_station: Dict[str, str]):
    """get a dict by county containing the cumulative rainfall
    for all months on record"""
    # get a `Path` to the data directory
    csv_directory = pathlib.Path(args.directory)

    rainfall_by_county: Dict[str, Dict[str, List[Any]]] = {}

    with open('data/stations.json', 'rt') as f:
        stations = json.load(f)

    # iterate through the county–station mapping
    for county, station in county_station.items():
        # get the correct station
        for s in stations[county]:
            if s['station'] != station:
                continue

            # construct the filepath
            filepath = csv_directory / s['filename']

            # load the DataFrame
            df = load_data(filepath, station=s)

            # get the cumulative rainfall for every month
            agg = df.groupby('year_month')['rain'].agg('sum')

            # convert the index to a string that can be serialised
            agg.index = agg.index.to_series().astype(str)

            # extract out the `year_month` and `rainfall` from the Series
            year_month, rainfall = zip(*agg.to_dict().items())

            # construct a dict containing all years, rainfall recorded,
            # and year_month values
            rainfall_by_county[county] = {
                'year': (
                    agg.index.str.extract('(\d{4})')
                    .astype(int)
                    .values
                    .flatten()
                    .tolist()
                ),
                'rainfall': list(rainfall),
                'year_month': list(year_month),
            }

    return rainfall_by_county


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='clean and transform historical weather data files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('directory', help='directory containing weather data')
    args = parser.parse_args()

    # get a mapping from county to station with the highest
    # number of records
    county_station = get_station_with_most_records()

    # write the data to disk
    with open('data/county_station.json', 'wt') as f:
        json.dump(county_station, f, indent=2)

    # get a mapping from county to cumulative rainfall by month
    rainfall_by_county = rainfall_year_month_by_county(county_station)

    # write the data to disk
    with open('data/rainfall_by_county.json', 'wt') as f:
        json.dump(rainfall_by_county, f, indent=2)
