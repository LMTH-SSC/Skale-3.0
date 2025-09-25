import base64
import random
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

CLIENT_ID = "848257adc4a646a2b9fb9f841c40bded"
CLIENT_SECRET = "adc674b08c97400681a78f18284014de"


def get_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"},
        timeout=10
    )
    r.raise_for_status()
    return r.json()["access_token"]


def pick_track(token, genres=["hiphop", "afrobeat"]):
    seed_artists = {
        "hiphop": ["Drake", "Kendrick Lamar", "Travis Scott", "J. Cole", "Kanye West"],
        "afrobeat": ["Burna Boy", "Wizkid", "Davido", "Rema", "Asake"]
    }
    genre = random.choice(genres)
    artist = random.choice(seed_artists[genre])

    search = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": artist, "type": "artist", "limit": 1},
        timeout=10
    )
    items = search.json().get("artists", {}).get("items", [])
    if not items:
        return None
    artist_id = items[0]["id"]

    top = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
        headers={"Authorization": f"Bearer {token}"},
        params={"market": "US"},
        timeout=10
    )
    tracks = top.json().get("tracks", [])
    if not tracks:
        return None

    tracks_with_images = [
        t for t in tracks if t.get("album", {}).get("images")]
    if not tracks_with_images:
        return None
    return random.choice(tracks_with_images)


@app.route("/question")
def question():
    token = get_token()
    track = pick_track(token)
    if not track:
        return jsonify({"error": "No track found"})

    return jsonify({
        "art_url": track["album"]["images"][0]["url"],
        "answer": f"{track['name']} - {track['artists'][0]['name']}"
    })


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
