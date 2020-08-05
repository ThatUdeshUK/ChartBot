#!/usr/bin/env python

"""Get charts from Last.FM API.
"""

import sys
import argparse
import requests
import json

from utility.files import WriteableDir, write_results

last_fm_base_url = 'http://ws.audioscrobbler.com/2.0/'
last_fm_api_key = '196e42e2e2c1a028450f5426a88a7fb4'


def gen_last_fm_url(method):
    return last_fm_base_url + '?method=' + method


def get_global_chart():
    url = f'{gen_last_fm_url("chart.gettoptracks")}&api_key={last_fm_api_key}&format=json'
    response = requests.get(url)
    charts = json.loads(response.text)

    def mapper(track):
        return {
            'name': track['name'],
            'play_count': track['name'],
            'artist': track['artist']['name']
        }

    top_tracks = list(map(mapper, charts['tracks']['track']))
    return top_tracks


def get_geo_chart(country):
    url = f'{gen_last_fm_url("geo.gettoptracks")}&country={country}&api_key={last_fm_api_key}&format=json'
    response = requests.get(url)
    charts = json.loads(response.text)
    return charts


def run(dataset_dir):
    lastfm_path = dataset_dir + '/lastfm.json'

    global_tracks = get_global_chart()

    write_results(lastfm_path, global_tracks)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('dir', help="Dataset directory",
                        action=WriteableDir, default='.')

    args = parser.parse_args(arguments)

    dataset_dir = args.dir
    run(dataset_dir)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
