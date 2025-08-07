import streamlit as st
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import gdown
import os

# -------------------- SETTINGS --------------------

# Replace these with your actual Google Drive file IDs
DF_FILE_ID = 'https://drive.google.com/file/d/1YrIpnVZzoeGtPl257ihH0ibEvz2FupT7/view?usp=drive_link'
SIMILARITY_FILE_ID = 'https://drive.google.com/file/d/1bRfyN6LyrZxI6-zi2quC9UxTYnrVU1AW/view?usp=drive_link'

# Spotify API credentials (from Spotify Developer Dashboard)
CLIENT_ID = "fc322433e3e7478785cdfc32775b77d1"
CLIENT_SECRET = "df79b11fb3564225b8fa143738a5121d"

# -------------------- FILE DOWNLOAD --------------------

def download_file(file_id, filename):
    url = f"https://drive.google.com/uc?id={file_id}"
    if not os.path.exists(filename):
        gdown.download(url, filename, quiet=False)

download_file(DF_FILE_ID, "df.pkl")
download_file(SIMILARITY_FILE_ID, "similarity.pkl")

# -------------------- LOAD DATA --------------------

with open('df.pkl', 'rb') as f:
    music = pickle.load(f)

with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

# -------------------- SPOTIFY SETUP --------------------

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        return track["album"]["images"][0]["url"]
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"  # Default image

# -------------------- RECOMMENDER FUNCTION --------------------

def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []

    for i in distances[1:7]:
        artist = music.iloc[i[0]].artist
        song_name = music.iloc[i[0]].song
        recommended_music_names.append(song_name)
        recommended_music_posters.append(get_song_album_cover_url(song_name, artist))

    return recommended_music_names, recommended_music_posters

# -------------------- STREAMLIT UI --------------------

st.set_page_config(page_title="Music Recommender", layout="wide")
st.title("🎵 Music Recommendation System")

music_list = music['song'].values
selected_song = st.selectbox("Type or select a song from the dropdown", music_list)

if st.button("Show Recommendation"):
    recommended_music_names, recommended_music_posters = recommend(selected_song)

    row1 = st.columns(3)
    for i in range(3):
        with row1[i]:
            st.image(recommended_music_posters[i])
            st.text(recommended_music_names[i])

    row2 = st.columns(3)
    for i in range(3, 6):
        with row2[i - 3]:
            st.image(recommended_music_posters[i])
            st.text(recommended_music_names[i])
