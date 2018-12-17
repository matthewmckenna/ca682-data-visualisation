# CA682: Data Management and Visualisation

Code and analyses for CA682 module.

## Data

Data will be hosted on Google Drive.

## Finding weather station data

Met Éireann provides access to historical data via their [website](https://www.met.ie/climate/available-data/historical-data).
The interface provided allows a user to download a dataset for one weather station at a time.
However, for this project we require much more data, and would like all data for all weather stations.

Using the inspection tools in Chrome I found a `stations.csv` file that was being loaded.
Some fields of interest here were the station name, county, latitude, longitude, and most importantly, the assigned station number.

I then found a base url where the historical data was hosted.
By manually downloading a single dataset and examining the URL, I was able to determine the form of the URLs for the hosted data:

`"$BASE_URL"/dly"$STATION_NUMBER".zip`

## Cleaning up `stations.csv`

There is a lot of information that we don't need in `stations.csv`.
This file can be tidied up to extract only the fields of interest by running `clean_stations_csv.sh`.
This is a very simple shell script.
The contents are shown below:

```bash
$ cat clean_stations_csv.sh
#!/bin/bash
# extract fields of interest from `stations.csv`

# directory containing the input file `stations.csv`
data_dir=$1

# the name of the input file
input_file="$1"/stations.csv
# the name of the output file
output_file="$1"/stations_clean.csv

# add the header to the output file
echo "station_number,station_name,county,latitude,longitude" >"$output_file"

# extract the first five fields of the input file, skip the original header
# and append the rest to the output file
cut -d',' -f1-5 "$input_file" |tail -n+2 >>"$output_file"
```

## Getting all weather station data

Run the Python application to download the data:

```bash
$ python get_data.py data/daily/zips
```

Note that the path passed (`data/daily/zips`) above, **must** exist.
With the example above, `518` zip archives were downloaded to `data/daily/zips`.
This took several minutes, running with two threads.

## Unzipping the archives

The zip archives were downloaded to `data/daily/zips`.
From the parent directory (`data/daily`), the following commands were run to extract the archives:

```bash
$ mkdir csvs
$ for f in $(ls zips); do unzip -nd csv zips/$f; done >log 2>&1
```

Some errors were noted during the `unzip` operation (as noted in the `log` file generated).
It appears that a number of the constructed URLs were not valid.
There are `20` files (listed below) for which the archive size is < 1 KB, and simply contain the source of a `404` error page.

```bash
$ find . -type f -size -1024c
./dly3422.zip
./dly9938.zip
./dly2931.zip
./dly538.zip
./dly9323.zip
./dly4413.zip
./dly3037.zip
./dly1807.zip
./dly4702.zip
./dly2604.zip
./dly199.zip
./dly5819.zip
./dly5602.zip
./dly9206.zip
./dly8912.zip
./dly2218.zip
./dly8123.zip
./dly5729.zip
./dly9106.zip
./dly907.zip
```

This leaves us with valid weather data for `498` weather stations across Ireland.


## Finding how many rows to skip

The CSV files are not standardised.
In order to load the CSVs into a `DataFrame`, we need to provide the `skiprows` argument.
In order to find out how many rows to skip, we can recursively `grep` for the header line.
In the `data` directory, run:

```bash
grep -nr "date," daily/csvs/dly*.csv |cut -d'/' -f3 |cut -d':' -f1,2 >header_rows.txt
```

We can inspect the first `10` lines with:

```bash
$ head header_rows.txt
dly10023.csv:10
dly1024.csv:10
dly1033.csv:10
dly1042.csv:10
dly1043.csv:10
dly1075.csv:25
dly108.csv:10
dly1103.csv:10
dly1107.csv:10
dly1108.csv:10
```

For most of the files, the header is on line `10`.
However, for `dly1075.csv`, the header is on line `25`.
We can extract this information, and create a mapping using Python.
We'll also make use of the `stations_clean.csv` file generated earlier.

## Data shift in `stations.csv`

There is an extra comma in the `county` field in the original `stations.csv` which caused the data to be shifted when running the script to clean this data.
This can be corrected by running the following code on macOS:

```bash
$ sed -i.bak "460s/.*/5331,DELVIN CASTLE G.C.,Westmeath,53.608,-7.104/" stations_clean.csv
$ mv stations_clean.csv{.bak,}
```

or on Linux/Windows

```bash
$ sed -i "460s/.*/5331,DELVIN CASTLE G.C.,Westmeath,53.608,-7.104/" stations_clean.csv
```


## Creating a `DataFrame` with all station details

We want to gather all information about the stations in an easy-to-use format.
We'll use `pandas` to create `DataFrame` objects to work with.
Initial cleaning and transformation is done in [`data-cleaning_2018-12-14.ipynb`](data-cleaning_2018-12-14.ipynb).
