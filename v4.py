import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading
import yt_dlp
from youtube_search import YoutubeSearch
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TPE2, TALB, TDRC, TRCK, TCON, TPUB, error
import urllib.request
import os
import re

# Configuración de autenticación de Spotify
SPOTIFY_CLIENT_ID = "5561376fd0234838863a8c3a6cbb0865"
SPOTIFY_CLIENT_SECRET = "fa12e995f56c48a28e28fb056e041d18"
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, 
    client_secret=SPOTIFY_CLIENT_SECRET))

def clean_title(title):
    title = re.sub(r'\(.*?\)|\[.*?\]', '', title)  # Elimina paréntesis y corchetes
    title = re.sub(r'(?i)official (video|lyrics|audio|music video)', '', title)
    title = re.sub(r'(?i)lyric video', '', title)
    title = re.sub(r'[^a-zA-Z0-9 \-]', '', title)  # Elimina caracteres especiales
    return title.strip()

def custom_title(s):
    # Capitaliza solo la primera letra de cada palabra sin modificar letras tras un apóstrofe
    return ' '.join(word[0].upper() + word[1:].lower() if word else '' for word in s.split())

def get_best_youtube_url(song, artist, duration):
    search_query = f"{artist} - {song}"
    results = YoutubeSearch(search_query, max_results=5).to_dict()
    best_url = None
    min_diff = float('inf')
    
    for result in results:
        video_duration = result.get('duration', "0:00")
        video_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(video_duration.split(':'))))
        diff = abs(video_seconds - duration)
        if diff < min_diff:
            min_diff = diff
            best_url = f"https://www.youtube.com{result['url_suffix']}"
    
    return best_url

def my_progress_hook(info):
    if info['status'] == 'downloading':
        total = info.get('total_bytes') or info.get('total_bytes_estimate')
        if total:
            percent = info['downloaded_bytes'] * 100 / total
            progress_var.set(percent)
            root.update_idletasks()
    elif info['status'] == 'finished':
        progress_var.set(100)
        root.update_idletasks()

def download_song(song, artist, save_path, progress_var):
    results = spotify.search(q=f"track:{song} artist:{artist}", type="track", limit=1)
    if not results['tracks']['items']:
        messagebox.showerror("Error", f"No se encontró la canción en Spotify: {song} - {artist}")
        return
    
    track = results['tracks']['items'][0]
    correct_title = custom_title(track['name'])
    correct_artist = custom_title(track['artists'][0]['name'])
    album = track['album']['name']
    album_artist = track['album']['artists'][0]['name']
    release_year = track['album']['release_date'].split("-")[0]
    track_number = track['track_number']
    genre = ', '.join(track['album'].get('genres', [])) or "Unknown"
    publisher = track['album'].get('label', 'Unknown')
    duration = track['duration_ms'] // 1000
    album_cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None
    
    video_url = get_best_youtube_url(correct_title, correct_artist, duration)
    if not video_url:
        messagebox.showerror("Error", f"No se encontró un video adecuado para: {correct_title} - {correct_artist}")
        return
    
    filename = f"{correct_artist} - {correct_title}"
    filename = clean_title(filename)
    filepath = os.path.join(save_path, filename)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filepath,  # Se descarga sin extensión visible
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'progress_hooks': [my_progress_hook]
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(video_url, download=True)
    
    filepath += ".mp3"
    if os.path.exists(filepath) and album_cover_url:
        cover_filename = os.path.join(save_path, "cover.jpg")
        urllib.request.urlretrieve(album_cover_url, cover_filename)
        
        audio = MP3(filepath, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass
        
        with open(cover_filename, 'rb') as img:
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=0,  # cover front
                desc='Cover',
                data=img.read()
            ))
        
        audio.tags.add(TIT2(encoding=3, text=correct_title))
        audio.tags.add(TPE1(encoding=3, text=[a['name'] for a in track['artists']]))
        audio.tags.add(TPE2(encoding=3, text=album_artist))
        audio.tags.add(TALB(encoding=3, text=album))
        audio.tags.add(TDRC(encoding=3, text=release_year))
        audio.tags.add(TRCK(encoding=3, text=str(track_number)))
        audio.tags.add(TCON(encoding=3, text=genre))
        audio.tags.add(TPUB(encoding=3, text=publisher))
        
        audio.save(v2_version=3)
        os.remove(cover_filename)
    
    progress_var.set(100)
    root.update_idletasks()
    # Actualiza el Listbox para mostrar la tilde verde
    idx = song_list.index((song, artist))
    current_text = listbox.get(idx)
    listbox.delete(idx)
    listbox.insert(idx, current_text + " ✔")

def start_download():
    save_path = filedialog.askdirectory()
    if not save_path:
        return
    for i, (song, artist) in enumerate(song_list):
        progress_var.set(0)
        download_song(song, artist, save_path, progress_var)
    messagebox.showinfo("Completado", "Descarga finalizada.")
    listbox.delete(0, tk.END)
    song_list.clear()

def add_song():
    song = song_entry.get()
    artist = artist_entry.get()
    if song and artist:
        song_list.append((song, artist))
        listbox.insert(tk.END, f"{artist} - {song}")
        song_entry.delete(0, tk.END)
        artist_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Ingrese la canción y el artista.")

def remove_song():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        listbox.delete(index)
        song_list.pop(index)

def download_thread():
    threading.Thread(target=start_download).start()

# Interfaz gráfica
root = tk.Tk()
root.title("Descargador de Canciones")

song_list = []

frame = tk.Frame(root)
frame.pack(pady=10)

song_label = tk.Label(frame, text="Canción:", font=("Arial", 12))
song_label.grid(row=0, column=0)
song_entry = tk.Entry(frame, width=30, font=("Arial", 12))
song_entry.grid(row=0, column=1)

artist_label = tk.Label(frame, text="Artista:", font=("Arial", 12))
artist_label.grid(row=1, column=0)
artist_entry = tk.Entry(frame, width=30, font=("Arial", 12))
artist_entry.grid(row=1, column=1)

add_button = tk.Button(frame, text="Agregar", font=("Arial", 12), command=add_song)
add_button.grid(row=2, columnspan=2, pady=5)

listbox = tk.Listbox(root, width=50, height=10, font=("Arial", 12))
listbox.pack()

remove_button = tk.Button(root, text="Eliminar", font=("Arial", 12), command=remove_song)
remove_button.pack(pady=5)

download_button = tk.Button(root, text="Descargar", font=("Arial", 12), command=download_thread)
download_button.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=5, fill=tk.X)

import threading
root.mainloop()
