from django.shortcuts import render, redirect
from django.http import HttpResponse
from dotenv import load_dotenv
from time import sleep
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
    context = {}
    if request.method == 'POST':
        playlist_url = request.POST.get('url', '')
        if playlist_url:
            playlist_id = playlist_url[34:56]
            audio_features = get_playlist_info(playlist_id)
            openai_prompt = generate_openai_prompt(audio_features)
            prompt = openai_prompt[0]
            colorscheme = openai_prompt[1]
            emotion = openai_prompt[2]

            openai_response = get_openai_response(prompt)
            image_prompts = openai_response.split(",")
            
            context['image_url_1'] = generate_dalle_image(image_prompts[0], colorscheme, emotion)
            context['image_url_2'] = generate_dalle_image(image_prompts[1][1:], colorscheme, emotion)
            context['image_url_3'] = generate_dalle_image(image_prompts[2], colorscheme, emotion)

            return render(request, 'results.html', context)
    return render(request, 'index.html')


def results(request):
    image_url_1 = request.GET.get('image_url_1', '')
    image_url_2 = request.GET.get('image_url_2', '')
    image_url_3 = request.GET.get('image_url_3', '')

    context = {
        'image_url_1': image_url_1,
        'image_url_2': image_url_2,
        'image_url_3': image_url_3,
    }
    return render(request, 'results.html', context)


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
#   translator = str.maketrans("", "", string.punctuation)
  return response_content #.translate(translator)


def generate_dalle_image(openai_reponse, colorscheme, emotion):
    prompt = emotion + " " + openai_reponse + " in " + colorscheme + " colors and in the illustration style of Hayao Miyazaki"
    print(prompt)
    image_response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="256x256" #'256x256', '512x512', '1024x1024', '1024x1792', '1792x1024'
    )
    image_url = image_response['data'][0]['url']
    print(image_url)
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

    acousticness = label_value(sum(acousticness)/len(acousticness))
    danceability = label_value(sum(danceability)/len(danceability))
    energy = label_value(sum(energy)/len(energy))
    instrumentalness = label_value(sum(instrumentalness)/len(instrumentalness))
    #avg_key = sum(key)/len(key)
    liveness = label_value(sum(liveness)/len(liveness))
    #avg_mode = sum(mode)/len(mode)
    #avg_speechiness = sum(speechiness)/len(speechiness)
    tempo = sum(tempo)/len(tempo)
    time_signature = sum(time_signature)/len(time_signature)
    valence = label_value(sum(valence)/len(valence))

    if energy == "low":
        colorscheme = "muted"
    elif energy == "medium":
        colorscheme = "pastel"
    else:
        colorscheme = "bright"
    
    if liveness == "low":
        emotion = "serene"
    elif liveness == "medium":
        emotion = "comforting"
    else:
        emotion = "dynamic"

    openai_prompt = "in 3-8 words, give me three different images or objects, separated by commas, that represent a song with " + acousticness + "accousticness , " + danceability + "danceability, " + energy + "energy, " + instrumentalness + "instrumentalness, " + liveness  + "liveness, tempo of " + str(tempo) + " bpm, time signature of " + str(time_signature) + ", and " + valence + "valence"
    
    return openai_prompt, colorscheme, emotion


def label_value(value):
    if value >= 0.7:
        return "high"
    elif value >= 0.5:
        return "medium"
    else:
        return "low"


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
