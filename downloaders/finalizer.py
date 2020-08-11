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


def gen_title(title):
    return title.split("(")[0].split("[")[0]


def trim(top, video_path, width, height, forced=False):
    top_videos = top

    for video in top_videos:
        video_out_path = video_path + video['data']['id'] + '_trimmed.mp4'
        if forced or not os.access(video_out_path, os.R_OK):
            video_file_path = video_path + video['data']['id'] + '.video'
            audio_file_path = video_path + video['data']['id'] + '.audio'
            if os.access(video_file_path, os.R_OK) and os.access(audio_file_path, os.R_OK):
                start_time = duration_to_start(video['data']['duration'])
                inputs = f'-i {video_file_path} -i {audio_file_path}'
                timing = f'-ss {start_time} -t 10'
                scaling = f'-vf \"scale=-1:{height},pad={width}:ih:(ow-iw)/2\"'
                command = f'ffmpeg -y {inputs} {timing} {scaling} {video_out_path}'
                print(command)
                os.system(command)
        else:
            print("Trimmed file exists")


def create_overlays(top, video_path, width, height, limit):
    x_pos = 300
    y_pos = (height / 2) - 200

    count = 0
    for top_video in top:
        top_video_path = video_path + top_video['data']['id'] + '_intro.mp4'
        ffmpeg.input(video_path + 'overlay.mp4') \
            .drawtext(text=count + 1, x=x_pos, y=y_pos, box=1, fontcolor='white', fontsize=128, boxborderw=16,
                      boxcolor='black') \
            .drawtext(text=gen_title(top_video['data']['title']), x=x_pos, y=y_pos + 160, box=1, fontsize=96,
                      boxborderw=16) \
            .output(top_video_path) \
            .run(overwrite_output=True)
        count += 1
        if count >= limit:
            break
    if count < limit:
        print("Not enough videos to make a chart")


def concat(top, video_path, width, height, limit):
    top_videos = []

    count = 0
    for top_video in top:
        top_video_path = video_path + top_video['data']['id'] + '_trimmed.mp4'
        top_video_overlay_path = video_path + top_video['data']['id'] + '_intro.mp4'
        if os.access(top_video_path, os.R_OK) and os.path.getsize(top_video_path) > 10:
            top_video['path'] = top_video_path
            top_video['overlay_path'] = top_video_overlay_path
            top_video['pos'] = count + 1
            top_videos.append(top_video)
            count += 1
        if count >= limit:
            break
    if count < limit:
        print("Not enough videos to make a chart")

    top_videos.reverse()

    def mapper(video):
        y_pos = height - 160
        x_pos = 100
        video_input = ffmpeg.input(video['path'])
        overlay_input = ffmpeg.input(video['overlay_path'])

        video_video = video_input.video \
            .drawtext(text=str(video['pos']), x=x_pos, y=y_pos - 60, box=1, fontsize=28, boxborderw=16, boxcolor='red') \
            .drawtext(text=gen_title(video['data']['title']), x=x_pos, y=y_pos, box=1, fontsize=28, boxborderw=16) \
            .overlay(overlay_input.video, eof_action='pass')

        video_audio = video_input.audio

        return [video_video, video_audio]

    split_streams = map(mapper, top_videos)

    streams = list(chain.from_iterable(split_streams))

    joined = ffmpeg.concat(*streams, v=1, a=1).node
    v = joined[0]
    a = joined[1].filter('volume', 0.8)
    ffmpeg.output(v, a, video_path + 'output.mp4').run(overwrite_output=True)


def run(dataset_dir, width, height, limit, forced):
    reduced_path = dataset_dir + '/selected.json'
    video_path = dataset_dir + '/videos/'

    if not os.access(reduced_path, os.R_OK):
        print("Dataset required from URL extraction is not available on the given directory")
        return

    if not os.path.exists(video_path):
        os.makedirs(video_path)

    with open(reduced_path, 'r') as json_data:
        top = json.load(json_data)

    trim(top, video_path, width, height, forced)
    create_overlays(top, video_path, width, height, limit)
    concat(top, video_path, width, height, limit)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-f', '--force', type=bool, default=False)
    parser.add_argument('-vw', '--width', type=int, default=1920)
    parser.add_argument('-vh', '--height', type=int, default=1080)
    parser.add_argument('-l', '--limit', type=int, default=20)
    parser.add_argument('dir', help="Dataset directory",
                        action=WriteableDir, default='.')

    args = parser.parse_args(arguments)

    forced = args.force
    width = args.width
    height = args.height
    limit = args.limit
    dataset_dir = args.dir

    run(dataset_dir, width, height, limit, forced)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
