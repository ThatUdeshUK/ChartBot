#!/usr/bin/env python

"""Download reduced YouTube videos.
"""

import os
import sys
import argparse
import json
import pafy
import ffmpeg
import youtube_dl

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir

youtube_video_url = 'https://www.youtube.com/watch?v='


def download(youtube, video_path):
    skipped = 0
    for video in youtube:
        url = youtube_video_url + video['data']['id']
        audio_file_path = video_path + video['data']['id'] + '.audio'
        video_file_path = video_path + video['data']['id'] + '.webm'

        if os.access(audio_file_path, os.R_OK) and os.access(video_file_path, os.R_OK):
            print("Files exists", video['data']['id'])
            continue

        try:
            video_data = pafy.new(url)
        except youtube_dl.utils.ExtractorError:
            skipped += 1
            continue

        print(video_data)

        print(video_data.videostreams)

        best_video = list(
            filter(lambda s: str(s).find('1080') != -1 and str(s).find('webm') != -1, video_data.videostreams))
        if len(best_video) > 0:
            best_video = best_video[0]
        else:
            best_video = video_data.getbestvideo('webm', True)

        best_audio = video_data.getbestaudio()
        print(best_video, 'X', best_audio)

        if best_audio and best_video:
            print(best_video.get_filesize())
            try:
                best_audio.download(audio_file_path)
                best_video.download(video_file_path)
            except youtube_dl.utils.ExtractorError:
                skipped += 1
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
