import pandas as pd
import json
import glob
import os
import requests
import spotipy.util as util

filepath = '/Users/seoyeonhong/MyData'
output_path = '/Users/seoyeonhong/Desktop/IMT543'

# User Information
user_columns = ['username', 'email', 'country', 'birthdate', 'gender' \
                'postalCode', 'creationTime']

f = open(filepath + '/Userdata.json')
user_data = json.load(f)

user_dict = {}

for k in user_data:
    if k in user_columns:
        user_dict[k] = [user_data[k]]

user_df = pd.DataFrame(user_dict, columns = user_columns)
user_df.to_csv(output_path + 'user_df.csv')

# Playlist

files = glob.glob(filepath + '/Playlist*.json')

playlist_dict = {'PlaylistName': [],
                 'LastModifiedDate': [],
                 'Description': [],
                 'trackName': [],
                 'artistName': [],
                 'albumName': [],
                 'trackUri': []}

for file in files:
    f = open(file)
    playlist_data = json.load(f)
    for playlist in playlist_data['playlists']:
        num = 0
        for track in playlist['items']:
            num += 1
            playlist_dict['trackName'].append(track['track']['trackName'])
            playlist_dict['artistName'].append(track['track']['artistName'])
            playlist_dict['albumName'].append(track['track']['albumName'])
            playlist_dict['trackUri'].append(track['track']['trackUri'])
        playlist_dict['PlaylistName'].extend([playlist['name']]*num)
        playlist_dict['LastModifiedDate'].extend([playlist['lastModifiedDate']]*num)
        playlist_dict['Description'].extend([playlist['description']]*num)

playlist_df = pd.DataFrame(playlist_dict, columns = playlist_dict.keys())
playlist_df.to_csv(output_path + 'playlist_df.csv')

# Streaming History

files = glob.glob(filepath + '/StreamingHistory*.json')

history_dict = {'endTime': [],
                'artistName': [],
                'trackName': [],
                'msPlayed': []}

for file in files:
    f = open(file)
    history_data = json.load(f)
    for item in history_data:
        history_dict['endTime'].append(item['endTime'])
        history_dict['artistName'].append(item['artistName'])
        history_dict['trackName'].append(item['trackName'])
        history_dict['msPlayed'].append(item['msPlayed'])

history_df = pd.DataFrame(history_dict, columns = history_dict.keys())
history_df.to_csv(output_path + 'history_df.csv')

# Spotify API

# Authorizing Spotify API Access

username = '31rqxcgr3ded573dcrahj46fkyxq'
scope = 'user-library-read'

token = util.prompt_for_user_token(username=username, 
                                   scope = scope, 
                                   client_id = os.environ.get('SPOTIPY_CLIENT_ID'),   
                                   client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET'),     
                                   redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI'))

# Playlist - Get track info of songs in playlist

def get_track(id):
    if 'spotify:track:' in id:
        id = id[14:]

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
    }

    response = requests.get(f'https://api.spotify.com/v1/tracks/{id}', headers=headers)
    json = response.json()
    
    # Return variables
    result = {}

    result['track_uri'] = json['uri']
    result['track_duration'] = json['duration_ms']
    result['track_popularity'] = json['popularity']

    result['album_id'] = json['album']['id']
    result['album_type'] = json['album']['album_type']
    result['album_name'] = json['album']['name']
    result['album_releasedate'] = json['album']['release_date']
    result['album_totaltracks'] = json['album']['total_tracks']
    result['album_uri'] = json['album']['uri']

    result['artist_id'] = []
    result['artist_name'] = []
    result['artist_uri'] = []

    for artist in json['album']['artists']:
        result['artist_id'].append(artist['id'])
        result['artist_name'].append(artist['name'])
        result['artist_uri'].append(artist['uri'])

    return result

def get_audio_features(id):
    if 'spotify:track:' in id:
        id = id[14:]
 
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
    }

    response = requests.get(f'https://api.spotify.com/v1/audio-features/{id}', headers=headers)

    # Return Variables
    result = response.json()
    result['id'] = id

    return result


def get_artist(id):
    if 'spotify:track:' in id:
        id = id[14:]

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
    }

    response = requests.get(f'https://api.spotify.com/v1/artists/{id}', headers=headers)
    json = response.json()
    
    # Return variables
    result = {}

    result['uri'] = json['uri']
    result['artist_name'] = json['name']
    result['artist_popularity'] = json['popularity']
    result['follower_num'] = json['followers']['total']
    result['genres'] = json['genres']

# Extracting track info for playlist tracks

rows = []

for track in playlist_df.trackUri:
    try:
        result = get_track(track)
    except:
        print(f'Error at track URI {track}')
    rows.append(result)

playlist_songs = pd.DataFrame.from_dict(rows, orient = 'columns')

print('Playlist track info extracted')

playlist_songs.to_csv(output_path + 'playlist_songs.csv')

# Extracting audio features for playlist tracks

rows = []

for track in playlist_df.trackUri:
    try:
        result = get_audio_features(track)
    except:
        print(f'Error at track URI {track}')
    rows.append(result)

audio_features = pd.DataFrame.from_dict(rows, orient = 'columns')

print('Audio Features info extracted')

audio_features.to_csv(output_path + 'audio_features.csv')

# Extracting artist info for playlist tracks

rows = []

for artists in playlist_songs.artist_id:
    for artist in artists:
        try:
            result = get_artist(artist)
        except:
            print(f'Error at artist URI {artist}')
        rows.append(result)

artists = pd.DataFrame.from_dict(rows, orient = 'columns')

print('Artist info extracted')

artists.to_csv(output_path + 'artists.csv')
