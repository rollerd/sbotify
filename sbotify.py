import pylast
import time
import requests
import json
import spotipy
import logging

logging.basicConfig(filename='/var/log/sbotify/sbotify_error.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

API_KEY = " "
API_SECRET = " "
SLACK_WEBHOOK_URL = " "

username = " "
password_hash = pylast.md5(" ")


def connect_lastfm():
    network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET, username = username, password_hash = password_hash)
    logging.info('Created network object')
    return network


def get_user(network):
    myuser = network.get_user(username)

    return myuser


def get_currently_playing(user):
    now_playing = user.get_now_playing()

    return now_playing


def send_to_slack(now_playing):
    link, cover_url,track = get_spotify_info(now_playing)

    if not link:
        return None # last.fm API erroneously reports no currently playing song from time to time

    now_playing = "Now listening to: {0} : <{1}>".format(str(now_playing), link + '|{0}'.format(track.decode('ascii', 'ignore')))
    payload = {"text":now_playing}
    post_data = json.dumps(payload)
    r = requests.post(SLACK_WEBHOOK_URL, data=post_data)
    print r.text


def get_spotify_info(now_playing):
    try:
        artist = now_playing.get_artist().name
        track = now_playing.get_title()
        album = now_playing.get_album().get_title()
        cover_img_url = now_playing.get_album().get_cover_image()
    except AttributeError as e:
        logging.warn('Attribute error: {0}'.format(e))
        return None, None, None

    sp = spotipy.Spotify()

    try:
        result = sp.search(q='artist:{0} album:{1} track:{2}'.format(artist, album, track))
    except UnicodeEncodeError as e: # got lazy - will fix this up
        logging.warn('Encoding issues')
        artist = artist.encode('utf-8')
        album = album.encode('utf-8')
        track = track.encode('utf-8')
        result = sp.search(q='artist:{0} album:{1} track:{2}'.format(artist, album, track))

    link_to_track = result['tracks']['items'][0]['external_urls']['spotify']

    return link_to_track, cover_img_url, track


def main_loop(network):
    user_status = {} # {username : [song, last_update], ...}

    while 1:

        with open('users.txt', 'r') as f:
            data = f.readlines()

            for username in data:
                username = username.strip()
                user_object = network.get_user(username)

                last_update = user_status.get(username, [None, time.time() - 45])[1]

                current_time = time.time()

                if current_time - 40 > last_update:

                    try:
                        now_playing = user_object.get_now_playing()

                        if now_playing == user_status.get(username, [None, time.time()])[0] or now_playing == None:
                            logging.info('No change in status for user: {0} Song: {1}'.format(username, now_playing))
                            user_status[username] = [now_playing, time.time()]
                        else:
                            logging.info('User {0} changed status: Song is now: {1} - sending update to Slack'.format(username, str(now_playing)))
                            user_status[username] = [now_playing, time.time()]
                            send_to_slack(now_playing)


                    except pylast.WSError as e:
                        print 'User {0} not found'.format(username)

                time.sleep(1) # API allows one call per second


if __name__=="__main__":
    network = connect_lastfm()
    main_loop(network)
