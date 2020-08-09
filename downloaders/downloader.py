#!/usr/bin/env python

"""Download reduced YouTube videos.
"""

import os
import sys
import argparse
import json
import pafy

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir

youtube_video_url = 'https://www.youtube.com/watch?v='


def download(youtube, video_path):
    skipped = 0
    for video in youtube:
        url = youtube_video_url + video['data']['id']
        video_data = pafy.new(url)
        print(video_data)
        streams = video_data.streams
        if len(streams) > 0:
            stream = streams[0]
            print(stream.get_filesize())
            stream.download(video_path + video['data']['id'] + '.mp4')
        else:
            skipped += 1


def run(dataset_dir):
    reduced_path = dataset_dir + '/selected.json'
    video_path = dataset_dir + '/videos/'

    if not os.access(reduced_path, os.R_OK):
        print("Dataset required from URL extraction is not available on the given directory")
        return

    if not os.path.exists(video_path):
        os.makedirs(video_path)

    with open(reduced_path, 'r') as json_data:
        youtube = json.load(json_data)

    download(youtube, video_path)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-y', '--youtube', help="YouTube Data API key")
    parser.add_argument('dir', help="Dataset directory",
                        action=WriteableDir, default='.')

    args = parser.parse_args(arguments)

    api_key = args.youtube
    pafy.set_api_key(api_key)

    dataset_dir = args.dir

    run(dataset_dir)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
