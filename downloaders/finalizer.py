#!/usr/bin/env python

"""Download reduced YouTube videos.
"""

import os
import sys
import argparse
import json
from datetime import time
import ffmpeg
from itertools import chain

sys.path.append(os.path.dirname(__file__) + "/..")
from utility.files import WriteableDir


def duration_to_start(duration):
    print(duration)
    mins_split = duration[2:].split("M")
    mins = int(mins_split[0])
    sec_split = mins_split[1].split("S")
    sec = 0
    if len(sec_split) > 0 and sec_split[0] != '':
        sec = int(sec_split[0])
    start_time = time(0, mins - 1, sec)
    return str(start_time)


def trim(top, video_path, forced=False):
    top_videos = top

    for video in top_videos:
        video_out_path = video_path + video['id'] + '_trimmed.mp4'
        if forced or not os.access(video_out_path, os.R_OK):
            video_file_path = video_path + video['id'] + '.mp4'
            if os.access(video_file_path, os.R_OK):
                start_time = duration_to_start(video['data']['duration'])
                command = "ffmpeg -y -i " + video_file_path + " -ss  " + start_time + " -t " + str(
                    10) + " -vf \"scale=-1:360,pad=640:ih:(ow-iw)/2\" " + video_out_path
                os.system(command)
        else:
            print("Trimmed file exists")


def concat(top, video_path, limit=20):
    top_videos = []

    count = 0
    for top_video in top:
        top_video_path = video_path + top_video['id'] + '_trimmed.mp4'
        if os.access(top_video_path, os.R_OK) and os.path.getsize(top_video_path) > 10:
            top_video['path'] = top_video_path
            top_video['pos'] = count + 1
            top_videos.append(top_video)
            count += 1
        if count >= limit:
            break
    if count < limit:
        print("Not enough videos to make a chart")

    top_videos.reverse()

    def mapper(video):
        video_input = ffmpeg.input(video['path'])

        def gen_title(title):
            return title.split("(")[0]

        video_video = video_input.video \
            .drawtext(text=str(video['pos']), x=40, y=260, box=1, boxborderw=8, boxcolor='red') \
            .drawtext(text=gen_title(video['data']['title']), x=40, y=290, box=1, boxborderw=8)

        video_audio = video_input.audio

        return [video_video, video_audio]

    split_streams = map(mapper, top_videos)

    streams = list(chain.from_iterable(split_streams))

    joined = ffmpeg.concat(*streams, v=1, a=1).node
    v = joined[0]
    a = joined[1].filter('volume', 0.8)
    ffmpeg.output(v, a, video_path + 'output.mp4').run(overwrite_output=True)


def run(dataset_dir):
    reduced_path = dataset_dir + '/reduced.json'
    video_path = dataset_dir + '/videos/'

    if not os.access(reduced_path, os.R_OK):
        print("Dataset required from URL extraction is not available on the given directory")
        return

    if not os.path.exists(video_path):
        os.makedirs(video_path)

    with open(reduced_path, 'r') as json_data:
        top = json.load(json_data)

    trim(top, video_path, False)
    concat(top, video_path)


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
