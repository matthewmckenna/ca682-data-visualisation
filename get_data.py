#!/usr/bin/env python
"""
download weather data from Met Éireann.
"""
import argparse
import pathlib
import pprint
from queue import Queue
import threading
import time
from typing import List

import requests

BASE_URL = 'https://cli.fusio.net/cli/climate_data/webdata'


def simple_threaded_download(
    urls: List[str],
    download_path: pathlib.Path,
    *,
    nthreads: int = 2,
    chunk_size: int = 32*1024,
    sleep: int = 1,
) -> None:
    """a simple threaded download helper"""
    threads = []
    q: Queue = Queue()

    options = {
        'chunk_size': chunk_size,
        'download_path': download_path,
        'sleep': sleep,
    }
    print(f'using options={options}')

    for _ in range(nthreads):
        t = threading.Thread(target=simple_download, args=(q,), kwargs=options)
        t.start()
        threads.append(t)

    for u in urls:
        q.put(u)

    for _ in range(nthreads):
        q.put(None)

    for t in threads:
        t.join()


def simple_download(
    q,
    *,
    chunk_size: int = 32*1024,
    download_path: pathlib.Path = pathlib.Path.home() / 'Downloads',
    sleep: int = 1,
):
    """download files"""
    while True:
        url = q.get()

        if url is None:
            return

        fname = url.rsplit('/')[-1]
        path = download_path / fname

        with open(path, 'wb') as f:
            r = requests.get(url)
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)

        time.sleep(sleep)


def get_daily_weather_station_data():
    """download daily weather station data"""
    # TODO: get `station_numbers` from `stations.csv`
    station_numbers = [2115, 375, 6114, 4515]
    urls = [f'{BASE_URL}/dly{station_num}.zip' for station_num in station_numbers]

    # TODO: check if `~` expands to user home on Windows
    download_path = pathlib.Path(args.directory)
    simple_threaded_download(
        urls,
        download_path=download_path,
        nthreads=2,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='download historical weather data files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('directory', help='download directory')
    args = parser.parse_args()
    get_daily_weather_station_data()
