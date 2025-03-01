from src.controller import MusicDownloaderController
from src.model import MusicDownloaderModel
from src.view import MusicDownloaderView

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()

    # Read the Spotify client ID and secret from a file
    with open("secret/spotify_secrets.txt") as f:
        client_id, client_secret = f.read().splitlines()

    model = MusicDownloaderModel(client_id, client_secret)
    view = MusicDownloaderView(root)
    controller = MusicDownloaderController(model, view)

    root.title("Music Downloader")
    root.geometry("400x300")

    root.mainloop()
