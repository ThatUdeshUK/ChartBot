#!/usr/bin/env python

"""Reduced data from Last.FM API and YouTube Data API.
"""

import os
import sys
import argparse
import json
from tqdm import tqdm

sys.path.append(os.path.dirname(__file__) + "/..")
from sources.youtube_api import YoutubeApi
from utility.files import WriteableDir, write_results, create_if_not_exist

youtube = YoutubeApi()


def youtube_reduce(reduced_data, youtube_data):
    print("Reducing Youtube")
    for video in tqdm(youtube_data):
        video_id = video['id']
        if video_id in reduced_data:
            if 'counts' not in reduced_data[video_id]:
                reduced_data[video_id]['counts'] = {}
            reduced_data[video_id]['counts']['yt'] = video['count']
        else:
            reduced_data[video_id] = {
                'data': video['data'],
                'counts': {
                    'yt': video['count']
                }
            }

    return reduced_data


def chart_reduce(reduced_data, chart, chart_data):
    print("Reducing", chart)
    for track in tqdm(chart_data):
        video_id = track['youtube_id']
        if not video_id:
            continue

        if video_id in reduced_data:
            if 'pos' not in reduced_data[video_id]:
                reduced_data[video_id]['pos'] = {}
            reduced_data[video_id]['pos'][chart] = track['pos']
        else:
            reduced_data[video_id] = {
                'data': youtube.get_video(video_id),
                'pos': {chart: track['pos']}
            }

    return reduced_data


def run(dataset_dir, api_key):
    youtube_path = dataset_dir + '/youtube.json'
    lastfm_path = dataset_dir + '/lastfm.json'
    uk40_path = dataset_dir + '/uk40.json'
    at40_path = dataset_dir + '/at40.json'
    reduced_path = dataset_dir + '/reduced.json'

    youtube.set_api_key(api_key)

    create_if_not_exist(reduced_path, {})

    with open(reduced_path, 'r') as json_data:
        reduced_data = json.load(json_data)

    if os.access(youtube_path, os.R_OK):
        with open(youtube_path, 'r') as json_data:
            youtube_data = json.load(json_data)

        reduced_data = youtube_reduce(reduced_data, youtube_data)
        write_results(reduced_path, reduced_data)

    if os.access(lastfm_path, os.R_OK):
        with open(lastfm_path, 'r') as json_data:
            lastfm_data = json.load(json_data)

        reduced_data = chart_reduce(reduced_data, 'lastfm', lastfm_data)
        write_results(reduced_path, reduced_data)

    if os.access(uk40_path, os.R_OK):
        with open(uk40_path, 'r') as json_data:
            uk40_data = json.load(json_data)

        reduced_data = chart_reduce(reduced_data, 'uk40', uk40_data)
        write_results(reduced_path, reduced_data)

    if os.access(at40_path, os.R_OK):
        with open(at40_path, 'r') as json_data:
            at40_data = json.load(json_data)

        reduced_data = chart_reduce(reduced_data, 'at40', at40_data)
        write_results(reduced_path, reduced_data)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-y', '--youtube', help="YouTube Data API key")
    parser.add_argument('dir', help="Dataset directory",
                        action=WriteableDir, default='.')

    args = parser.parse_args(arguments)

    api_key = args.youtube
    dataset_dir = args.dir

    run(dataset_dir, api_key)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
