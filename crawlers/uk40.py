#!/usr/bin/env python

"""Scrape UK Top 40 chart.
"""

import os
import sys
import argparse
import requests
import json
from bs4 import BeautifulSoup as bs, element

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir, write_results

uk40_base_url = 'https://www.officialcharts.com/charts/uk-top-40-singles-chart/'


def get_chart():
    response = requests.get(uk40_base_url)

    chart_bs = bs(response.text, features="html5lib")
    chart_items_bs = chart_bs.select('.track')

    chart = []
    for item in chart_items_bs:
        title = item.select('.title')[0].contents[1].contents[0]
        artist = item.select('.artist')[0].contents[1].contents[0]

        chart.append({
            'title': title.lower(),
            'artist': artist.lower()
        })

    return chart


def run(dataset_dir):
    at40_path = dataset_dir + '/uk40.json'

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
