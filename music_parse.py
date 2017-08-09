#!/usr/bin/env python3
##
# Dakara Project
#

from karaneko.nekoparse import NekoParseMusic, NekoParseTagsGeneric, ConventionError
from warnings import warn

TAGS_DICT = {
        tag[0]: tag[2] for tag in NekoParseTagsGeneric.TAGS_BASE
        }

def extract_tags(tags):
    """ From the genre dictionnary, returns list of tags
    """ 
    tags_list = []

    for tag_attr, tag_name in TAGS_DICT.items():
        if getattr(tags, tag_attr):
            tags_list.append(tag_name)

    return tags_list

def parse_file_name(file_name):
    """ From a file name, returns a dictionnary with revelant values 
    """
    result = {}
    music = NekoParseMusic(file_name)
    music.parse()

    result['title_music'] = music.title_music
    result['version'] = music.extras.version
    result['detail'] = music.details
    result['artists'] = music.singers
    result['artists'].extend(music.composers)
    if music.extras.original_artist:
        result['artists'].append(music.extras.original_artist)

    extras = music.extras
    detail_video_list = []
    if extras.video:
        detail_video_list.append(extras.video)

    if extras.amv:
        detail_video_list.append(extras.amv)

    if extras.title_video:
        detail_video_list.append(extras.title_video)

    result['detail_video'] = ', '.join(detail_video_list)

    result['tags'] = extract_tags(music.tags)

    return result
