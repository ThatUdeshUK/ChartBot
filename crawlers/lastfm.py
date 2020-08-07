#!/usr/bin/env python

"""Get charts from Last.FM API.
"""

import os
import sys
import argparse
import requests
import json

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir, write_results

last_fm_base_url = 'http://ws.audioscrobbler.com/2.0/'


def gen_last_fm_url(method):
    return last_fm_base_url + '?method=' + method


def get_global_chart(api_key):
    url = f'{gen_last_fm_url("chart.gettoptracks")}&api_key={api_key}&format=json'
    response = requests.get(url)
    charts = json.loads(response.text)

    def mapper(track):
        return {
            'title': track['name'],
            'play_count': track['playcount'],
            'artist': track['artist']['name']
        }

    top_tracks = list(map(mapper, charts['tracks']['track']))
    return top_tracks


def get_geo_chart(api_key, country):
    url = f'{gen_last_fm_url("geo.gettoptracks")}&country={country}&api_key={api_key}&format=json'
    response = requests.get(url)
    charts = json.loads(response.text)
    return charts


def run(dataset_dir, api_key):
    lastfm_path = dataset_dir + '/lastfm.json'

    global_tracks = get_global_chart(api_key)

    write_results(lastfm_path, global_tracks)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-a', '--apikey', help="YouTube Data API key")
    parser.add_argument('dir', help="Dataset directory",
                        action=WriteableDir, default='.')

    args = parser.parse_args(arguments)

    api_key = args.apikey
    dataset_dir = args.dir

    run(dataset_dir, api_key)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
