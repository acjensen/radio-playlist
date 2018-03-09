

#
# Get a short audio recording of live radio from a website
#
import time, sys
from urllib.request import urlopen
#url = "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p"
url = 'http://crystalout.surfernetwork.com:8001/WHPI-FM_MP3'
print ("Connecting to "+url)
response = urlopen(url, timeout=10.0)
fname = "Sample"+str(time.clock())[2:]+".wav"
f = open(fname, 'wb')
block_size = 1024
print ("Recording roughly 10 seconds of audio Now - Please wait")
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
print ("10 seconds from "+url+" have been recorded in "+fname)


#
# Identify the track and return spotify unique id
#
from acrcloud.recognizer import ACRCloudRecognizer
import json
config = {
    'host': 'identify-us-west-2.acrcloud.com',
    'access_key': '82640bba7076975b5fcaf79d00795d16',
    'access_secret': 'JaLNPFDhjQbAuJyQKU8HfU6xZU2YzwzTFFiPH3Z7',
    'debug': True,
    'timeout': 10
}
acrcloud = ACRCloudRecognizer(config)
track_data = json.loads(acrcloud.recognize_by_file(fname, 0))
try:
    track_title = track_data['metadata']['music'][0]['external_metadata']['spotify']['track']['name']
    track_id = track_data['metadata']['music'][0]['external_metadata']['spotify']['track']['id']
    print('Title:', track_title)
    print('Spotify ID:', track_id)
except NoMetadata:
    print('No metadata found for '+track_title)

#
# Add the track to spotify playlist
#
import pprint
import sys
import spotipy
import spotipy.util as util

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
    results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
    print(results)
else:
    print("Can't get token for", username)
