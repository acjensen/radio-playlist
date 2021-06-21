import time, sys
from urllib.request import urlopen
from acrcloud.recognizer import ACRCloudRecognizer
import json
import os
import glob
import pprint
import sys
import spotipy
import spotipy.util as util

# Get a short audio recording of live radio from a website.
url = 'http://18363.live.streamtheworld.com/WZSTFM.mp3?tdtok=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6ImZTeXA4In0.eyJpc3MiOiJ0aXNydiIsInN1YiI6IjIxMDY0IiwiaWF0IjoxNTM3MDM4NjY0LCJ0ZC1yZWciOmZhbHNlfQ.aB_AKuD_Vwmu_3t8poeAoWq9E2K_aJfVz8piMpKZeis'
print ("Connecting to "+url)
response = urlopen(url, timeout=10.0)
fname = "Sample"+str(time.clock())[2:]+".wav"
f = open(fname, 'wb')
block_size = 1024
print ("Recording roughly 10 seconds of audio now - Please wait")
limit = 10
start = time.time()
while time.time() - start < limit:
    try:
        audio = response.read(block_size)
        if not audio:
            break
        f.write(audio)
        sys.stdout.write('.')
        sys.stdout.flush()
    except Exception as e:
        print ("Error "+str(e))
f.close()
sys.stdout.flush()
print("")
print("10 seconds from "+url+" have been recorded in "+fname)


# Identify the track and return it's unique Spotify id.
config = {
    'host': 'identify-us-west-2.acrcloud.com',
    'access_key': '82640bba7076975b5fcaf79d00795d16',
    'access_secret': 'JaLNPFDhjQbAuJyQKU8HfU6xZU2YzwzTFFiPH3Z7',
    'debug': True,
    'timeout': 10
}
acrcloud = ACRCloudRecognizer(config)
track_data = json.loads(acrcloud.recognize_by_file(fname, 0))
# Cleanup .wav
for f in glob.glob('*.wav'): os.remove(f)
try:
    track_title = track_data['metadata']['music'][0]['external_metadata']['spotify']['track']['name']
    track_id = track_data['metadata']['music'][0]['external_metadata']['spotify']['track']['id']
    print('Identified track as', '\"'+track_title+'\"', track_id)
except:
    print('Audio could not be identified')
    sys.exit()


# Add the track to a spotify playlist.
username = 'ajpieface2'
playlist_id = '0YNiCpiDoBymDKZSGSOaMa'
client_id = '10432503769b49b99aecc7acf15c1821'
client_secret = 'a1c5ce5b2d80496f91ed6210182bbff2'
redirect_uri = 'http://localhost/'
track_ids = [track_id]

scope = 'playlist-modify-public'
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    sp.user_playlist_remove_all_occurrences_of_tracks(username, playlist_id, track_ids)
    sp.user_playlist_add_tracks(username, playlist_id, track_ids)
    print('\"'+track_title+'\"', '('+track_id+')', 'added to playlist '+playlist_id)

else:
    print("Can't get token for", username)
