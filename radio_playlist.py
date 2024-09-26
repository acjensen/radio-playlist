import time, sys
from typing import Tuple
from urllib.request import urlopen
from acrcloud.recognizer import ACRCloudRecognizer
import json
import os
import glob
import sys
import spotipy
import spotipy.util as util
from datetime import datetime, timezone
from dataclasses import dataclass
from secret import ARC, Spotify


@dataclass
class Track:
    id: str
    title: str


@dataclass
class IdentifyTrackResponse:
    track_was_identified: bool
    track: Track


# Get a short audio recording of live radio from a website.
def record_https_live_stream(url: str) -> str:
    if url.startswith("http://"):
        raise Exception("HTTP is not supported")
    print("Connecting to " + url)
    response = urlopen(url, timeout=10.0)
    file_name = "sample_" + str(time.time()) + ".wav"
    f = open(file_name, "wb")
    block_size = 1024
    print(f"Beginning audio recording to file {file_name}")
    limit = 10
    start = time.time()
    while time.time() - start < limit:
        try:
            audio = response.read(block_size)
            if not audio:
                break
            f.write(audio)
            sys.stdout.write(".")
            sys.stdout.flush()
        except Exception as e:
            print("Error " + str(e))
    f.close()
    sys.stdout.flush()
    print("Finished audio recording")
    return file_name


# Identify the track and return it's unique Spotify id.
def identify_track(
    file_name: str, acr_cloud_recognizer_config: dict
) -> IdentifyTrackResponse:
    acr_cloud_recognizer = ACRCloudRecognizer(acr_cloud_recognizer_config)
    track_data = json.loads(acr_cloud_recognizer.recognize_by_file(file_name, 0))
    # Cleanup .wav
    for f in glob.glob("*.wav"):
        os.remove(f)
    try:
        track_title = track_data["metadata"]["music"][0]["external_metadata"][
            "spotify"
        ]["track"]["name"]
        track_id = track_data["metadata"]["music"][0]["external_metadata"]["spotify"][
            "track"
        ]["id"]
        print(f"Identified track as {track_title} with track ID {track_id}")
        return IdentifyTrackResponse(True, Track(track_id, track_title))
    except:
        print("Audio could not be identified")
        return IdentifyTrackResponse(False, None)


# Add the track to a spotify playlist.
def add_track_to_spotify_playlist(
    track_id: str,
    track_title: str,
    username: str,
    playlist_id: str,
    client_id: str,
    client_secret: str,
) -> None:
    redirect_uri = "http://localhost/"
    track_ids = [track_id]
    scope = "playlist-modify-public"
    token = util.prompt_for_user_token(
        username, scope, client_id, client_secret, redirect_uri
    )
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        sp.user_playlist_remove_all_occurrences_of_tracks(
            username, playlist_id, track_ids
        )
        sp.user_playlist_add_tracks(username, playlist_id, track_ids)
        print(
            f"Track {track_title} with track ID {track_id} added to playlist {playlist_id}"
        )
    else:
        raise Exception(f"Can't get token for spotify username {username}")


if __name__ == "__main__":
    while True:
        recording_file_name = record_https_live_stream(
            url="https://streams.kcrw.com/e24_mp3?aw_0_1st.playerid=TuneIn"
        )

        response = identify_track(
            recording_file_name,
            acr_cloud_recognizer_config={
                "host": "identify-us-west-2.acrcloud.com",
                "access_key": ARC.access_key,
                "access_secret": ARC.access_secret,
                "debug": True,
                "timeout": 10,
            },
        )

        if response.track_was_identified:
            add_track_to_spotify_playlist(
                track_id=response.track.id,
                track_title=response.track.title,
                username="ajpieface2",
                playlist_id="7AtOc3xyf6868NmRGgy6aP",
                client_id=Spotify.client_id,
                client_secret=Spotify.client_secret,
            )

        time.sleep(60)  # assume most tracks are at least 1 minute long
