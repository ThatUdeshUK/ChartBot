#!/usr/bin/env python

"""YouTube Data API.
"""

import sys
import googleapiclient.discovery

yt_api_service_name = "youtube"
yt_api_version = "v3"


class YoutubeApi:
    youtube = None

    def set_api_key(self, api_key):
        self.youtube = googleapiclient.discovery.build(
            yt_api_service_name, yt_api_version, developerKey=api_key)

    def get_top_music(self, region):
        if not self.youtube:
            raise Exception("Api key not set")

        request = self.youtube.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=region,
            videoCategoryId="10",
            maxResults=50
        )

        response = request.execute()

        def mapper(video):
            return {
                'id': video['id'],
                'duration': video['contentDetails']['duration'],
                'title': video['snippet']['title'],
                'publishedAt': video['snippet']['publishedAt'],
                'channelId': video['snippet']['channelId'],
                'statistics': video['statistics']
            }

        return list(map(mapper, response['items']))

    def get_video(self, video_id):
        if not self.youtube:
            raise Exception("Api key not set")

        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )

        response = request.execute()

        def mapper(video):
            return {
                'id': video['id'],
                'duration': video['contentDetails']['duration'],
                'title': video['snippet']['title'],
                'publishedAt': video['snippet']['publishedAt'],
                'channelId': video['snippet']['channelId'],
                'statistics': video['statistics']
            }

        if len(response['items']) > 0:
            return list(map(mapper, response['items']))[0]
        else:
            return None


def main(arguments):
    youtube = YoutubeApi()
    youtube.set_api_key('AIzaSyApZSllh8X0aggJ_qyXliX2yDiQU_9fgeA')

    # chart = youtube.get_top_music('US')
    video = youtube.get_video('AY1bA23hGMU')

    print(video)
    pass


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
