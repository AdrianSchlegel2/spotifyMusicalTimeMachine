from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

URL = "https://playback.fm/charts/top-100-songs/"


def ask_for_input():
    user_input = input("What year would you like to travel to? (between 1900 and 2021): ")

    try:
        user_input = int(user_input)
        if user_input > 2021 or user_input < 1900:
            print("Your number is not in the correct range")
            ask_for_input()
        else:
            return user_input
    except ValueError:
        print("You have not entered a valid number")
        ask_for_input()


year = ask_for_input()
response = requests.get(f"{URL}{year}")
content = response.text
soup = BeautifulSoup(content, "html.parser")

all_songs = soup.find_all(name="a", itemprop="name")
all_song_titles = [soup.getText().replace("\n", "") for soup in all_songs]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.environ["client_id"],
        client_secret=os.environ["client_secret"],
        redirect_uri="http://example.com",
        username=os.environ["username"],
        scope="playlist-modify-private",
        cache_path="token.txt",
        show_dialog=True,
    ))

user_id = sp.current_user()["id"]

spotify_song_URIs = []

for song in all_song_titles:
    result = sp.search(q=f"track: {song}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        spotify_song_URIs.append(uri)
    except IndexError:
        print("List index out of range")

playlist = sp.user_playlist_create(user=user_id, name=f"{year} Playback Top 100", public=False)


sp.playlist_add_items(
    playlist_id=playlist["id"],
    items=spotify_song_URIs,
)

