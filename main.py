from src.controller import MusicDownloaderController
from src.model import MediaManager
from src.view import MusicDownloaderView

import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()

    # Read the Spotify client ID and secret from a file
    with open("secret/spotify_secrets.txt") as f:
        client_id, client_secret = f.read().splitlines()

    model = MediaManager()
    controller = MusicDownloaderController(model, client_id, client_secret)
    view = MusicDownloaderView(root, controller)

    root.title("Music Downloader")
    root.geometry("720x480")

    root.mainloop()
