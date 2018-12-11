# CA682: Data Management and Visualisation

Code and analyses for CA682 module.

## Data

Data will be hosted on Google Drive.

## Finding weather station data

Met Éireann provides access to historical data via their [website](https://www.met.ie/climate/available-data/historical-data).
The interface provided allows a user to download a dataset for one weather station at a time. However, for this project we require much more data, and would like all data for all weather stations.

Using the inspection tools in Chrome I found a `stations.csv` file that was being loaded. Some fields of interest here were the station name, county, latitude, longitude, and most importantly, the assigned station number.

I then found a base url where the historical data was hosted. By manually downloading a single dataset, and examining the URL, I was able to determine the form of the URLs for the hosted data:

`"$BASE_URL"/dly"$STATION_NUMBER".zip`

## Getting all weather station data
