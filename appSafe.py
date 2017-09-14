from flask import Flask
from flask_ask import Ask, statement
import sh
import time
import sys
import spotipy
import spotipy.util as util
import unicodedata
import keys
from fuzzywuzzy import process

app = Flask(__name__)
ask = Ask(app, '/')
SPOTIPY_CLIENT_ID= keys.CLIENT_ID
SPOTIPY_CLIENT_SECRET = keys.CLIENT_SECRET
def ensureSP():
    try:
        sh.sp()
    except:
        proc = sh.spotify(_bg=True)
        time.sleep(3)
@ask.intent('SpotifyCommandIntent')
def spotify(command):
    ensureSP()
    if command == 'play' or command == 'pause':
        sh.sp(command)
        return statement('')
    elif command in ['skip', 'next', 'skip forwards']:
        sh.sp('next')
        return statement('')
    elif command in ['previous', 'skip backwards']:
        sh.sp('prev')
        sh.sp('prev')
        return statement('')
    return statement('an error occurred handling the request')

@ask.intent('SpotifyWhichSongIntent')
def whichSong():
    try:
        sh.sp()
    except:
        return statement('Spotify is not running right now')
    l = sh.sp('metadata').split('\n')
    m = {}
    for item in l:
        arr = item.rpartition('|')
        m[arr[0]] = arr[2]
    res = "playing %s, by %s" %(unicodedata.normalize('NFKD',m['title']).encode('ascii', 'ignore'),
            unicodedata.normalize('NFKD', m['artist']).encode('ascii', 'ignore'))
    return statement(res)

@ask.intent('SpotifyListPlaylistsIntent')
def playlistList():
    mscope = 'user-library-read'
    token = util.prompt_for_user_token(keys.CLIENT_NAME, scope=mscope, client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET)
    if token:
        instance = spotipy.Spotify(auth=token)
        pl = instance.user_playlists(keys.CLIENT_NAME)
        if len(pl['items']) == 0:
            return statement('you have no public playlists to choose from')
        s = "here are your playlists"
        for item in pl['items']:
            tmp = ", %s" %unicodedata.normalize('NFKD', item['name']).encode('ascii', 'ignore')
            s += tmp
        return statement(s)
    else:
        return statement('couldn\'t grab playlists for the user')

@ask.intent('SpotifyPlaylistIntent')
def playPlaylist(playlist):
    ensureSP()
    mscope = 'user-library-read'
    token = util.prompt_for_user_token(keys.CLIENT_NAME, scope=mscope, client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET)
    if token:
        instance = spotipy.Spotify(auth=token)
        pl = instance.user_playlists(keys.CLIENT_NAME)
        m = {}
        if len(pl['items']) == 0:
            return statement('there are no playlists available')
        for item in pl['items']:
            m[item['name']] = item['uri']
        playlist = process.extractOne(playlist, m.iterkeys())[0]
        uri = m[playlist]
        sh.sp('open', uri)
        return statement('')

@ask.intent('MomUpdateIntent')
def momStatus(momstatus):
    ensureSP()
    mscope = 'user-library-read'
    token = util.prompt_for_user_token(keys.CLIENT_NAME, scope=mscope, client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET)
    if token:
        instance = spotipy.Spotify(auth=token)
        pl = instance.user_playlists(keys.CLIENT_NAME)
        m = {}
    if len(pl['items']) == 0:
        return statement('there are no playlists available')
    for item in pl['items']:
        m[item['name']] = item['uri']

    if momstatus in ['home', 'back']:
        sh.amixer('-D', 'pulse', 'sset' , 'Master', '30%')
        playlist = process.extractOne('xmas acapella', m.iterkeys())[0]
        uri = m[playlist]
        sh.sp('open', uri)
        return statement('')
    elif momstatus == 'gone':
        sh.amixer('-D', 'pulse', 'sset' , 'Master', '70%')
        playlist = process.extractOne('no mother', m.iterkeys())[0]
        uri = m[playlist]
        sh.sp('open', uri)
        return statement('')

@ask.intent('SpotifySearchIntent')
def search(term):
    ensureSP()
    sh.sp('search', term)
    return statement('here\'s what I found for %s' %term)

if __name__ == '__main__':
    app.run()
