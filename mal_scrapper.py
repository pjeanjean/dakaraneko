#!/usr.bin/env python3
##
# Dakara Project
#

import json, html, os, re, requests

json_file_path = ''

def get_artists(tags, force_scrap=False):
    """
    Find and save the artists of an anime theme by scrapping MyAnimeList.
    The scrapped data will be cached to reduce later parsing times.

    tags is a dictionnary generated by anime_parse.parse_file_name (will be edited with the found artists)
    """

    # We don't care about IS
    if tags['link_type'] not in ['OP', 'ED']:
        return []

    global json_file_path
    json_file_path = os.path.dirname(os.path.realpath(__file__)) + '/mal_scrapper.json'

    # We first load the local data
    json_file = open(json_file_path, 'r')
    saved_data = json.load(json_file)
    json_file.close()

    # If we don't find the anime, let's scrap MAL
    scrapped = False
    if tags['title_work'] not in saved_data[0] or force_scrap: # We check if we don't already have the anime scrapped
        scrap_anime(tags['title_work'], saved_data)
        scrapped = True

    # If we find the anime, let's get the artists
    if tags['title_work'] in saved_data[0]:
        index = tags['link_nb']
        if index > 0: # The index is either 0, or n+1 (n being the theme we want)
            index = index - 1

        if index < len(saved_data[0][tags['title_work']][tags['link_type']]): # Index in list, we use it
            return saved_data[0][tags['title_work']][tags['link_type']][index]
        elif not scrapped: # Index not in list but no scrapping done... Local data may not be updated so we do it now
            return get_artists(tags, True)
        else: # Index not in list despite scrapping... Can't do anything else here
            return []
    else:
        return []


def scrap_anime(name, data):
    """
    This function does the actual scrapping and saves it in data.
    """

    # First steap: finding the page of the anime, using the search engine
    r = requests.get('https://myanimelist.net/anime.php?q=' + name)
    result = r.text
    found = {}

    i = 0
    N = 10 # Max number of results kept
    for entry in result.split('\n'):
        if '<a class="hoverinfo_trigger fw-b fl-l"' in entry:
            if i >= N: # We won't keep more than N entries
                break;
            i = i + 1

            anime = re.sub('^.*<strong>([^"]*)</strong>.*$', r'\1', entry)
            link = re.sub('^.*" href="([^"]*)".*$', r'\1', entry) 
            found[anime] = link # We store the result and continue

            if html.unescape(anime) == name: # If we find a perfect match, that's great!
                break
    
    if html.unescape(anime) != name: # If we didn't get a perfect match, we will ask the user
        i = 0
        animes_found = list(found)
        print()
        for i in range(len(animes_found)):
            print(str(i) + ": " + html.unescape(animes_found[i]))
        match_index = input(name + ": which is the right one? ")
        if (int(match_index) >= N): # No match, no need to continue
            return

        anime = animes_found[int(match_index)]

    # Second step: getting the page of the found anime
    r = requests.get(found[anime])
    result = r.text
    op = []
    ed = []

    # Third step: extracting the artists
    for line in result.split('\n'):
        if '<div class="theme-songs js-theme-songs opnening">' in line:
            op = extract_artists(line)
        if '<div class="theme-songs js-theme-songs ending">' in line:
            ed = extract_artists(line)

    # Fourth step: saving the data locally
    data[0][name] = {}
    data[0][name]['OP'] = op
    data[0][name]['ED'] = ed

    json_file = open(json_file_path, 'w')
    json.dump(data, json_file)
    json_file.close()


def extract_artists(line):
    """
    When scrapping, extracts the artists from the html line that contains them.
    """
    artists = []
    for entry in line.split('<br>'): # For each theme
        if entry != "</div>": # This ignores the last entry
            temp_artists = []
            found = re.sub('^.*&quot; by ([^<]*)</span>$', r'\1', entry) # This gets the artists
            found = re.sub(' \(ep.*\)$', '', found) # This removes the information about the episodes
            found = found.encode("ascii", errors="ignore").decode() # This removes the non ASCII characters
            found = re.sub(' \( *\)', '', found) # This removes the parenthesis with spaces only
            for artist in found.split(', '): # Here we split if there are multiple artists
                artist = re.sub('^.* \((.*)\)', r'\1', artist) # For the cases where the real artist is in parenthesis
                temp_artists.append(html.unescape(artist))
            artists.append(temp_artists)

    return artists
