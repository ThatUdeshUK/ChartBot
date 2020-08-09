#!/usr/bin/env python

"""Scrape UK Top 40 chart.
"""

import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

sys.path.append(os.path.dirname(__file__) + "/..")
from sources.lastfm_api import LastFMApi
from utility.files import WriteableDir, write_results

uk40_base_url = 'https://www.officialcharts.com/charts/uk-top-40-singles-chart/'


def get_chart():
    response = requests.get(uk40_base_url)

    chart_bs = bs(response.text, features="html5lib")
    chart_items_bs = chart_bs.select('.track')

    chart = []
    pos = 1
    for item in chart_items_bs:
        title = item.select('.title')[0].contents[1].contents[0]
        artist = item.select('.artist')[0].contents[1].contents[0]

        chart.append({
            'title': title.lower(),
            'artist': artist.lower(),
            'pos': pos
        })
        pos += 1

    return chart


def run(dataset_dir, api_key):
    at40_path = dataset_dir + '/uk40.json'

    lastfm = LastFMApi(api_key)

    chart = get_chart()

    searched_chart = []
    for track in tqdm(chart):
        trimmed_artist = track['artist'].split(" & ")[0].split(" ft ")[0].split(" feat.")[0]
        print(track['title'], ' - ', trimmed_artist)
        search_result = lastfm.search_track(track['title'], trimmed_artist)
        if search_result:
            search_result['pos'] = track['pos']
            searched_chart.append(search_result)

    write_results(at40_path, searched_chart)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-l', '--lastfm', help="YouTube Data API key")
    parser.add_argument('dir', help="Dataset directory",
                        action=WriteableDir, default='.')

    args = parser.parse_args(arguments)

    api_key = args.lastfm
    dataset_dir = args.dir

    run(dataset_dir, api_key)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
