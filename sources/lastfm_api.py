#!/usr/bin/env python

"""Last.FM API.
"""

import sys
import requests
import json
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

last_fm_base_url = 'http://ws.audioscrobbler.com/2.0/'


def gen_last_fm_url(method):
    return last_fm_base_url + '?method=' + method


def get_youtube_id(lastfm_url):
    response = requests.get(lastfm_url)

    track_bs = bs(response.text, features='html5lib')
    video_overlay_bs = track_bs.select('.js-video-preview-playlink')
    if len(video_overlay_bs) > 0:
        video_bs = video_overlay_bs[0].select('.image-overlay-playlink-link')[0]

        if 'data-youtube-id' in video_bs.attrs:
            return video_bs.attrs['data-youtube-id']


class LastFMApi:

    def __init__(self, api_key):
        self.api_key = api_key

    def get_global_chart(self):
        url = f'{gen_last_fm_url("chart.gettoptracks")}&api_key={self.api_key}&format=json'
        response = requests.get(url)
        charts = json.loads(response.text)

        def mapper(track):
            return {
                'title': track['name'],
                'play_count': track['playcount'],
                'artist': track['artist']['name'],
                'youtube_id': get_youtube_id(track['url'])
            }

        top_tracks = []
        for chart_track in tqdm(charts['tracks']['track']):
            top_tracks.append(mapper(chart_track))

        return top_tracks

    def search_track(self, title, artist):
        url = f'{gen_last_fm_url("track.search")}&track={title}&artist={artist}&limit=5&api_key={self.api_key}&format=json'
        response = requests.get(url)
        results = json.loads(response.text)

        def mapper(track):
            return {
                'title': track['name'],
                'artist': track['artist'],
                'listeners': track['listeners'],
                'url': track['url'],
                'youtube_id': None
            }

        search_results = list(map(mapper, results['results']['trackmatches']['track']))

        if len(search_results) > 0:
            result = search_results[0]
            result['youtube_id'] = get_youtube_id(result['url'])
            return result
        else:
            return None


def main(arguments):
    last_fm = LastFMApi('196e42e2e2c1a028450f5426a88a7fb4')

    # result = last_fm.get_global_chart()
    result = last_fm.search_track('past life', 'Trevor Daniel X Selena Gomez')
    print(result)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
