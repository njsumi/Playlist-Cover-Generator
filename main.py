from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    authorization_string = client_id + ":" + client_secret
    authorization_bytes = authorization_string.encode("utf-8")
    authorization_base64 = str(base64.b64encode(authorization_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + authorization_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)

    #convert json string into python dictionary to access info inside
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_authorization_header(token):
    return {"Authorization": "Bearer " + token}

def get_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_authorization_header(token)
    query = f"?q={artist_name}&type=artist&limit=1" #gives first artist that pops up when searching artist name

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"] #just gives us the individual artist
    if len(json_result) == 0:
        print("No artist with this name exists.")
        return None
    
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=KR"
    headers = get_authorization_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"] 
    return json_result

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_authorization_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    tracks = json_result.get('tracks', {}).get('items', [])
    return tracks

def get_tracks_audio_features(token, track_ids):
    url = f"https://api.spotify.com/v1/audio-features?ids={track_ids}"
    headers = get_authorization_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result


token = get_token()
tracks = get_playlist_tracks(token, "3BMylbkttS9hqjOsqoXwJT") # ?si=860de0e89be048bc
#print(tracks)

track_ids = ",".join(track['track']['id'] for track in tracks)
#print(track_ids)

audio_features = get_tracks_audio_features(token, track_ids)

#print(audio_features)
# for track in audio_features['audio_features']:
#     danceability = track['danceability']
#     print("Danceability:", danceability)

acousticness = []
for track in audio_features['audio_features']:
    acousticness.append(track['acousticness'])
danceability = []
for track in audio_features['audio_features']:
    danceability.append(track['danceability'])
energy = []
for track in audio_features['audio_features']:
    energy.append(track['energy'])
instrumentalness = []
for track in audio_features['audio_features']:
    instrumentalness.append(track['instrumentalness'])
key = []
for track in audio_features['audio_features']:
    key.append(track['key'])
liveness = []
for track in audio_features['audio_features']:
    liveness.append(track['liveness'])
mode = []
for track in audio_features['audio_features']:
    mode.append(track['mode'])
speechiness = []
for track in audio_features['audio_features']:
    speechiness.append(track['speechiness'])
tempo = []
for track in audio_features['audio_features']:
    tempo.append(track['tempo'])
time_signature = []
for track in audio_features['audio_features']:
    time_signature.append(track['time_signature'])
valence = []
for track in audio_features['audio_features']:
    valence.append(track['valence'])

avg_acousticness = sum(acousticness)/len(acousticness)
avg_danceability = sum(danceability)/len(danceability)
avg_energy = sum(energy)/len(energy)
avg_instrumentalness = sum(instrumentalness)/len(instrumentalness)
avg_key = sum(key)/len(key)
avg_liveness = sum(liveness)/len(liveness)
avg_mode = sum(mode)/len(mode)
avg_speechiness = sum(speechiness)/len(speechiness)
avg_tempo = sum(tempo)/len(tempo)
avg_time_signature = sum(time_signature)/len(time_signature)
avg_valence = sum(valence)/len(valence)

print("acousticness: ", avg_acousticness)
print("danceability: ", avg_danceability)
print("energy: ", avg_energy)
print("instrumentalness: ", avg_instrumentalness)
print("key: ", avg_key)
print("liveness: ", avg_liveness)
print("mode: ", avg_mode)
print("speechiness: ", avg_speechiness)
print("tempo: ", avg_tempo)
print("time signature: ", avg_time_signature)
print("valence: ", avg_valence)


# for index, track in enumerate(tracks):
#     track_name = track['track']['name']
#     track_artist = [artist['name'] for artist in track['track']['artists']]
#     artist = ', '.join(track_artist)
#     print(f"{index+1}. {track_name} by {artist}")

#result = get_artist(token, "IVE")
#artist_name = result["name"]
#artist_id = result["id"]
#songs = get_songs_by_artist(token, artist_id)

# for index, songs in enumerate(songs):
#     print(f"{index+1}. {songs['name']}")