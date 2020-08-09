#!/usr/bin/env python

"""Compile a chart by scoring and selecting tracks.
"""

import os
import sys
import argparse
import json
import pafy

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir, write_results

scores = {
    'yt': 1.5,
    'lastfm': 2,
    'at40': 3,
    'uk40': 3,
}


def count(reduced):
    for video_id, video_data in reduced.items():
        score = 0
        if 'pos' in video_data:
            if 'lastfm' in video_data['pos']:
                score += (50 - video_data['pos']['lastfm']) * scores['lastfm']
            if 'at40' in video_data['pos']:
                score += (50 - video_data['pos']['at40']) * scores['at40']
            if 'uk40' in video_data['pos']:
                score += (50 - video_data['pos']['uk40']) * scores['uk40']
        if 'counts' in video_data:
            score += video_data['counts']['yt'] * scores['yt']
        video_data['score'] = score
    return reduced


def run(dataset_dir):
    reduced_path = dataset_dir + '/reduced.json'
    selected_path = dataset_dir + '/selected.json'

    if not os.access(reduced_path, os.R_OK):
        print("Dataset required from URL extraction is not available on the given directory")
        return

    with open(reduced_path, 'r') as json_data:
        reduced = json.load(json_data)

    scored = count(reduced)
    selected = sorted(map(lambda x: x[1], scored.items()), key=lambda x: x['score'], reverse=True)[0:40]

    write_results(selected_path, selected)


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
