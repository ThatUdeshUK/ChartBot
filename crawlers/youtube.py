#!/usr/bin/env python

"""Get trending music videos from YouTube Data API.
"""

import os
import sys
import argparse

sys.path.append(os.path.dirname(__file__) + "/..")
from sources.youtube_api import YoutubeApi
from utility.files import WriteableDir, write_results


def get_top_music(api_key):
    youtube = YoutubeApi()
    youtube.set_api_key(api_key)

    regions = ['US', 'GB', 'AU', 'CA', 'AW', 'BE', 'SE']

    result = []

    for region in regions:
        print("Fetching top music from region:", region)
        region_chart = youtube.get_top_music(region)
        result.extend(region_chart)

    print(len(result))

    agg_videos = {}

    for selected_video in result:
        if selected_video['id'] in agg_videos:
            agg_videos[selected_video['id']]['count'] += 1
        else:
            agg_videos[selected_video['id']] = {
                'id': selected_video['id'],
                'data': selected_video,
                'count': 1
            }

    sorted_videos = sorted(map(lambda x: x[1], agg_videos.items()),
                           key=lambda x: (x['count'], x['data']['statistics']['viewCount']), reverse=True)
    print(len(sorted_videos))
    return sorted_videos


def run(dataset_dir, api_key):
    youtube_path = dataset_dir + '/youtube.json'

    videos = get_top_music(api_key)
    write_results(youtube_path, videos)


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
