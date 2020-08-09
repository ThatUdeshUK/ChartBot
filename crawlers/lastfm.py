#!/usr/bin/env python

"""Get charts from Last.FM API.
"""

import os
import sys
import argparse

sys.path.append(os.path.dirname(__file__) + "/..")
from sources.lastfm_api import LastFMApi
from utility.files import WriteableDir, write_results


def run(dataset_dir, lastfm_key):
    lastfm_path = dataset_dir + '/lastfm.json'

    lastfm = LastFMApi(lastfm_key)
    global_tracks = lastfm.get_global_chart()

    pos = 1
    for track in global_tracks:
        track['pos'] = pos
        pos += 1

    write_results(lastfm_path, global_tracks)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-l', '--lastfm', help="LastFm API key")
    parser.add_argument('dir', help="Dataset directory",
                        action=WriteableDir, default='.')

    args = parser.parse_args(arguments)

    lastfm_key = args.lastfm
    dataset_dir = args.dir

    run(dataset_dir, lastfm_key)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
