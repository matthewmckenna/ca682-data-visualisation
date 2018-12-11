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
