from django.shortcuts import render
from django.http import HttpResponse
from dotenv import load_dotenv
import os
import base64
import json
import requests
from requests import post, get
import openai
import string

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Create your views here.
def index(request):
    context = {
        'name': 'Nina'
    }

    if request.method == 'POST':
        playlist_url = request.POST.get('url', '')
        if playlist_url:
            playlist_id = playlist_url[34:56]
            audio_features = get_playlist_info(playlist_id)
            openai_prompt = generate_openai_prompt(audio_features)
            print(openai_prompt)
            openai_response = get_openai_response(openai_prompt)
            print(openai_response)
            image_response =  generate_dalle_image(openai_response)
            print(image_response)
            context['image_url'] = image_response
            


    return render(request, "index.html", context)


def get_openai_response(prompt):  
  openai.api_key = os.getenv("API_KEY")
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
  translator = str.maketrans("", "", string.punctuation)
  return response_content.translate(translator)

def generate_dalle_image(openai_reponse):
    prompt = openai_reponse + " image in the style of Hayao Miyazaki"
    print(prompt)
    image_response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = image_response['data'][0]['url']
    return image_url


def get_playlist_info(playlist_id):
    token = get_token()
    tracks = get_playlist_tracks(token, playlist_id)
    track_ids = ",".join(track['track']['id'] for track in tracks)
    audio_features = get_tracks_audio_features(token, track_ids)
    return audio_features

def generate_openai_prompt(audio_features):
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
    #avg_key = sum(key)/len(key)
    avg_liveness = sum(liveness)/len(liveness)
    #avg_mode = sum(mode)/len(mode)
    #avg_speechiness = sum(speechiness)/len(speechiness)
    avg_tempo = sum(tempo)/len(tempo)
    avg_time_signature = sum(time_signature)/len(time_signature)
    avg_valence = sum(valence)/len(valence)

    openai_prompt = "in 3-8 words, what image or object represents a song with " + label_value(avg_acousticness, "accousticness") + ", " + label_value(avg_danceability, "danceability") + ", " + label_value(avg_energy, "energy") + ", " + label_value(avg_instrumentalness, "instrumentalness") + ", " + label_value(avg_liveness, "liveness") + ", tempo of " + str(avg_tempo) + " bpm, time signature of " + str(avg_time_signature) + ", and " + label_value(avg_valence, "valence") + "?"
    return openai_prompt


def label_value(value, name):
    if 0.8 <= value <= 1:
        return "high " + name
    elif 0.4 <= value:
        return "medium " + name
    else:
        return "low " + name


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
