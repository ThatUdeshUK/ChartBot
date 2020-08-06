#!/usr/bin/env python

"""Get trending music videos from YouTube Data API.
"""

import os
import sys
import argparse
import googleapiclient.discovery

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir, write_results


def get_top_music(api_key, pages=1):
    yt_api_service_name = "youtube"
    yt_api_version = "v3"

    print("Discovering YouTube service")
    youtube = googleapiclient.discovery.build(
        yt_api_service_name, yt_api_version, developerKey=api_key)

    regions = ['US', 'GB', 'AU', 'CA', 'AW', 'BE', 'SE']

    result = []

    for region in regions:
        print("Fetching top music from region:", region)
        page_token = ""
        for i in range(pages):
            print("Fetching page No:", i + 1)
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode=region,
                videoCategoryId="10",
                maxResults=50,
                pageToken=page_token
            )

            response = request.execute()
            if 'nextPageToken' in response:
                print(response['nextPageToken'])
                page_token = response['nextPageToken']
            result.extend(response['items'])

    def mapper(video):
        return {
            'id': video['id'],
            'duration': video['contentDetails']['duration'],
            'title': video['snippet']['title'],
            'publishedAt': video['snippet']['publishedAt'],
            'channelId': video['snippet']['channelId'],
            'statistics': video['statistics']
        }

    print(len(result))

    selected = map(mapper, result)
    agg_videos = {}

    for selected_video in selected:
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

    videos = get_top_music(api_key, pages=2)
    write_results(youtube_path, videos)


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
