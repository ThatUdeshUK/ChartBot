#!/usr/bin/env python

"""Scrape AT40 chart.
"""

import os
import sys
import argparse
import requests
import json
from bs4 import BeautifulSoup as bs, element

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir, write_results

at40_base_url = 'https://www.at40.com/charts/top-40-238/latest/'


def get_chart():
    response = requests.get(at40_base_url)

    chart_bs = bs(response.text, features="html5lib")
    chart_items_bs = chart_bs.select('.component-chartlist-item')

    chart = []
    for item in chart_items_bs:
        title = item.select('.track-title')[0].contents[0]
        artist = item.select('.track-artist')[0].contents[0]

        chart.append({
            'title': title.lower(),
            'artist': artist.lower()
        })

    return chart


def run(dataset_dir):
    at40_path = dataset_dir + '/at40.json'

    chart = get_chart()

    write_results(at40_path, chart)


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
