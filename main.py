from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get
import openai
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import urllib.request
from PIL import Image
import numpy as np


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

playlist_url = "https://open.spotify.com/playlist/69DtCPWWYsZ7Zaq6avlbNH?si=74c5b6bd3e814cfa&nd=1"
playlist_id = playlist_url[34:56]

tracks = get_playlist_tracks(token, "3BMylbkttS9hqjOsqoXwJT") # ?si=860de0e89be048bc
#print(tracks)

track_ids = ",".join(track['track']['id'] for track in tracks)
#print(track_ids)

audio_features = get_tracks_audio_features(token, track_ids)
print("hello")
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

prompt = """in three to eight words describe a playlist with an average acousticness of {avg_acousticness} (range: 0-1), danceability of {avg_danceability} range: 0-1), energy of {avg_energy} (range: 0-1), instrumentalness of {avg_instrumentalness} (range: 0-1), key of {avg_key} (range: -1-11), liveness of {avg_liveness} (range: 0-1), mode of {avg_mode}, speechiness of {avg_speechiness} (range: 0-1), tempo of {avg_tempo} bpm, time signature of {avg_time_signature} (range: 3-7), and valence {avg_valence} (range: 0-1).""".format(avg_acousticness=avg_acousticness, avg_danceability=avg_danceability, 
                                                                            avg_energy=avg_energy, avg_instrumentalness=avg_instrumentalness, avg_key=avg_key, 
                                                                            avg_liveness=avg_liveness, avg_mode=avg_mode, avg_speechiness=avg_speechiness, 
                                                                            avg_tempo=avg_tempo, avg_time_signature=avg_time_signature, avg_valence=avg_valence)
print(prompt)

openai.api_key = os.getenv("API_KEY")

def get_openai_response(prompt):  
  result = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user",
        "content": prompt
      }
    ]
  )
    
  response_content = result.choices[0].message.content
  return response_content

#convert promt to lowercase and spaces are %20
response = get_openai_response(prompt).lower()
response += " image in studio ghibli style with no text"
print(response)

image_response = openai.Image.create(
  prompt="Acoustic guitar with gentle rhythmic movement image in studio ghibli style",
  n=1,
  size="1024x1024"
)
image_url = image_response['data'][0]['url']

image = Image.open(urllib.request.urlopen(image_url))
image_array = np.array(image)

plt.imshow(image_array)
plt.show()



