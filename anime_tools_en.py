# -*- coding:utf-8 -*-

import os
import re
from ffmpy import FFmpeg



def search_files(*path):
    video_count = 0
    sub_count = 0
    audio_count = 0
    rootdir = path[0]
    filelist = os.listdir(rootdir)
    videos = []
    subs = []
    audios = []
    for item in filelist:
        if item.endswith('.mkv') or item.endswith('.mp4'):
            videos.append(item)
            video_count += 1
        elif item.endswith('.ass') or item.endswith('.ssa') or item.endswith('.srt'):
            subs.append(item)
            sub_count += 1
        elif len(path) > 1:
            if item.endswith(path[1]):
                audios.append(item)
                audio_count += 1
    videos.sort()
    subs.sort()
    audios.sort()

    return videos, subs, audios, video_count, sub_count, audio_count


def match(videos, *sub_auds_des):
    pt = re.compile(r'(?:\s\-\s|\[|\(|\s|e|ep|EP)([0-9]{1,3})(?:\]|\)|\s|\.ass|\.srt|\.ssa|\.sub|\.mkv|\.mka|\.mp4|\.flac|\.m4v|\.acc)')
    pt2 = re.compile(r'\.(.*).ass|.srt|.ssa|.sub')
    video_sub = {}
    video_audio = {}

    for video in videos:
        multi_sub = []
        multi_sub_lan = []
        try:
            episode_v = re.findall(pt, video)[0]
            if sub_auds_des[1] == 's':
                if sub_auds_des[2] == 'y':
                    for sub in sub_auds_des[0]:
                        episode_s = re.findall(pt, sub)[0]
                        if episode_s == episode_v:
                            sub_lan = re.findall(pt2, sub)[0]
                            if not sub_lan in multi_sub_lan:
                                multi_sub.append(sub)
                                multi_sub_lan.append(sub_lan)
                    video_sub[video] = multi_sub
                elif sub_auds_des[2] == 'n':
                    for sub in sub_auds_des[0]:
                        episode_s = re.findall(pt, sub)[0]
                        if episode_s == episode_v and episode_v != '':
                            video_sub[video] = sub
            elif sub_auds_des[1] == 'a':
                for audio in sub_auds_des[0]:
                    episode_a = re.findall(pt, audio)[0]
                    if episode_a == episode_v and episode_v != '':
                        video_audio[video] = audio

        except:
            if sub_auds_des[1] == 's':
                if sub_auds_des[2] == 'y':
                    for sub in sub_auds_des[0]:
                        if os.path.splitext(video)[0] == os.path.splitext(sub)[0]:
                            sub_lan = re.findall(pt2, sub)[0]
                            if not sub_lan in multi_sub_lan:
                                multi_sub.append(sub)
                                multi_sub_lan.append(sub_lan)
                    video_sub[video] = multi_sub
                elif sub_auds_des[2] == 'n':
                    for sub in sub_auds_des[0]:
                        if os.path.splitext(video)[0] == os.path.splitext(sub)[0]:
                            video_sub[video] = sub
            elif sub_auds_des[1] == 'a':
                for audio in sub_auds_des[0]:
                    if os.path.splitext(video)[0] == os.path.splitext(audio)[0]:
                        video_audio[video] = audio
    return video_sub, video_audio


def merge_audio(path):
    path = path
    ext = input('Please enter the extension of the audio track, format：".xxx"（ignore quotation marks）')
    res = search_files(path, ext)
    videos = res[0]
    audios = res[2]
    video_audio = match(videos,audios, 'a')[1]
    i = 1
    for video in list(video_audio.keys()):
        ff = FFmpeg(
            executable='./ffmpeg.exe',
            inputs={path + video: None, path + video_audio[video]:None},
            outputs={path + '{}_merged_audio.mkv'.format(os.path.splitext(video)[0]): '-map 0 -map 1 -c copy'}
        )
        print('Mearging video NO.{} and it\'s audios'.format(i))
        print(ff.cmd)
        i += 1
        ff.run()


def rename(path):
    double = input('Is there multiple subtitile languages corrisponding to one video?(y/n)\n> ')
    res = search_files(path)
    videos = res[0]
    subs = res[1]
    video_count = 0
    sub_count = 0
    if double == 'y':
        video_sub = match(videos, subs, 's', 'y')[0]
        for video in list(video_sub.keys()):
            for sub in video_sub[video]:
                os.rename(path + sub, path + os.path.splitext(video)[0] + '.' + re.findall(r'\.(.*).ass|.srt|.ssa', sub)[0] + os.path.splitext(sub)[1])
                print(path + os.path.splitext(video)[0] + '.' + re.findall(r'\.(.*).ass|.srt|.ssa', sub)[0] + os.path.splitext(sub)[1])
                sub_count += 1
            video_count += 1
        print('All work done. Changed {} episodes，{} subtitiles'.format(video_count,sub_count))
    elif double == 'n':
        video_sub = match(videos, subs, 's', 'n')[0]
        for video in list(video_sub.keys()):
            os.rename(path + video_sub[video], path + os.path.splitext(video)[0] + os.path.splitext(video_sub[video])[1])
            print(path + os.path.splitext(video)[0] + os.path.splitext(video_sub[video])[1])
            video_count += 1
            sub_count += 1
        print('All work done. Changed {} episodes，{} subtitiles'.format(video_count,sub_count))
    else:
        print('invalid input, please try again')
    


def replace_audio(path):
    path = path
    ext = input('Please enter the extension of the audio track, format：".xxx"（ignore quotation marks）')
    res = search_files(path, ext)
    videos = res[0]
    audios = res[2]
    video_audio = match(videos,audios, 'a')[1]
    i = 1
    for video in list(video_audio.keys()):
        ff = FFmpeg(
            executable='./ffmpeg.exe',
            inputs={path + video: None, path + video_audio[video]:None},
            outputs={path + '{}_replaced_audio.mkv'.format(os.path.splitext(video)[0]): '-c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0'}
        )
        print('Repleasing video NO.{}'.format(i))
        print(ff.cmd)
        i += 1
        ff.run()




def main():
    print("anime tools v2.1".center(50,"-"),end="\n\n")
    path = input("Working directory(add'\\'to the end of the path, add '/' if you are using linux or Mac):")
    print("""
            Please select one of the following:
            1) Rename subtitiles to match videos
            2) Replease video's audio track with external audio track(one track)
            3) Merge external audio track into video(one track)
            more functions is comming
            """)
    correct_answer = False
    while not correct_answer:
        des = input("> ")
        if des == "1":
            rename(path)
            correct_answer = True
        elif des == "2":
            replace_audio(path)
            correct_answer = True
        elif des == "3":
            merge_audio(path)
            correct_answer = True
        else:
            print("invalid selection")

if __name__ == "__main__":
    main()
