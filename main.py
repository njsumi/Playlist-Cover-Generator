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




token = get_token()
tracks = get_playlist_tracks(token, "3BMylbkttS9hqjOsqoXwJT?si=860de0e89be048bc")
for index, track in enumerate(tracks):
    track_name = track['track']['name']
    track_artist = [artist['name'] for artist in track['track']['artists']]
    artist = ', '.join(track_artist)
    print(f"{index+1}. {track_name} by {artist}")

#result = get_artist(token, "IVE")
#artist_name = result["name"]
#artist_id = result["id"]
#songs = get_songs_by_artist(token, artist_id)

# for index, songs in enumerate(songs):
#     print(f"{index+1}. {songs['name']}")