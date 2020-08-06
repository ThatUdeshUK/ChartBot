#!/usr/bin/env python

"""Reduced data from Last.FM API and YouTube Data API.
"""

import os
import sys
import argparse
import json
from fuzzysearch import find_near_matches

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir, write_results


def summarize(youtube, lastfm):
    matches_count = 0
    for lastfm_track in lastfm:
        has_match = False
        for yt_track in youtube:
            lastfm_str = lastfm_track['name'].lower()
            yt_str = yt_track['data']['title'].lower()
            matched = find_near_matches(lastfm_str, yt_str, max_l_dist=0)
            if len(matched) > 0:
                print(lastfm_track['name'], "<>", yt_track['data']['title'])
                has_match = True
                yt_track['count'] += 1
        if has_match:
            matches_count += 1

    return youtube


def run(dataset_dir):
    youtube_path = dataset_dir + '/youtube.json'
    lastfm_path = dataset_dir + '/lastfm.json'
    reduced_path = dataset_dir + '/reduced.json'

    if not (os.access(youtube_path, os.R_OK) and os.access(youtube_path, os.R_OK)):
        print("Dataset required from URL extraction is not available on the given directory")
        return

    with open(youtube_path, 'r') as json_data:
        youtube = json.load(json_data)

    with open(lastfm_path, 'r') as json_data:
        lastfm = json.load(json_data)

    reduced = summarize(youtube, lastfm)
    reduced_sorted = sorted(reduced, key=lambda x: (x['count'], x['data']['statistics']['viewCount']), reverse=True)

    write_results(reduced_path, reduced_sorted)


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
