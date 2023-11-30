import streamlit as st
import pandas as pd
import pickle
import os
import base64
import random

path_to_dataset = "music_reco\music_reco\dataset.pkl"
path_to_model = "music_reco\music_reco\model.pkl"

# Modeli yükle
with open(path_to_model, 'rb') as model_file:
    tfidf_vectorizer = pickle.load(model_file)
    similarities = pickle.load(model_file)

df = pd.read_pickle(path_to_dataset)


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpeg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True
    )


add_bg_from_local('vinyl-2-wallpaper-1366x768.jpg')


def get_recommendations(song_index):
    song_similarities = similarities[song_index]
    top_similar_song_indices = song_similarities.argsort()[::-1][1:6]
    return df.loc[top_similar_song_indices]


def display_recommendations(recommendations):
    for idx, (_, row) in enumerate(recommendations.iterrows()):
        artist = row['artist_name']
        track = row['track_name']
        album = row['album_name']
        cover_image_url = row['album_image_url']
        spotify_url = row['track_uri'].replace("/track/", "/embed/track/")

        col1, col2 = st.columns([0.75, 1])

        with col1:
            st.image(cover_image_url, width=150)
            st.write(f"**Sanatçı:** {artist}")
            st.write(f"**Şarkı:** {track}")
            st.write(f"**Albüm:** {album}")

        with col2:
            st.write(
                f'<iframe src="{spotify_url}" width="350" height="180" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>',
                unsafe_allow_html=True
            )

        if idx < len(recommendations) - 1:
            st.markdown("✂➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")


def create_playlist_from_artists(artists):
    song_indices = []
    for artist in artists:
        artist_songs_df = df[df['artist_name'] == artist]
        if len(artist_songs_df) <= 3:
            song_indices.extend(artist_songs_df.index.tolist())
        else:
            song_indices.extend(artist_songs_df.sample(3).index.tolist())

    return df.loc[song_indices]


st.title('🎵 NotAI 🎵')

song = st.selectbox('Bir şarkı seçin', (df['artist_name'] + " - " + df['track_name']).unique())

if st.button('Öneri Al'):
    song_index = df[(df['artist_name'] + " - " + df['track_name']) == song].index[0]
    recommendations = get_recommendations(song_index)
    display_recommendations(recommendations)

artists_to_select = df['artist_name'].unique().tolist()
selected_artists = st.multiselect('Sevdiğin Sanatçılardan Playlist Oluşturabilirsin!', artists_to_select,
                                  default=artists_to_select[:3])

if len(selected_artists) < 3 or len(selected_artists) > 5:
    st.warning("Lütfen en az 3 ve en fazla 5 sanatçı seçin!")
else:
    if st.button('Playlist Hazırla'):
        playlist = create_playlist_from_artists(selected_artists)
        display_recommendations(playlist)

