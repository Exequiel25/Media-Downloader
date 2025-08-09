from src.controller import MusicDownloaderController
from src.model import MediaManager
from src.view import MusicDownloaderView

import tkinter as tk
from tkinter import simpledialog, messagebox
import os


def get_spotify_credentials():
    if os.path.exists("secret/spotify_secrets.txt"):
        with open("secret/spotify_secrets.txt") as f:
            return f.read().splitlines()
    else:
        root = tk.Tk()
        root.withdraw()  # Oculta la ventana principal
        messagebox.showinfo(
            "Spotify API",
            "Ingrese por favor sus claves de Spotify API para obtener metadatos."
        )
        client_id = simpledialog.askstring("Spotify API", "Client ID:")
        client_secret = simpledialog.askstring("Spotify API", "Client Secret:")
        if client_id and client_secret:
            os.makedirs("secret", exist_ok=True)
            with open("secret/spotify_secrets.txt", "w") as f:
                f.write(f"{client_id}\n{client_secret}")
            root.destroy()
            return [client_id, client_secret]
        else:
            continuar = messagebox.askyesno(
                "Continuar sin datos",
                "¿Desea continuar sin claves de Spotify? No se obtendrán metadatos."
            )
            root.destroy()
            if continuar:
                return [None, None]
            else:
                exit()


if __name__ == "__main__":
    client_id, client_secret = get_spotify_credentials()

    root = tk.Tk()
    model = MediaManager()
    controller = MusicDownloaderController(model, client_id, client_secret)
    view = MusicDownloaderView(root, controller)

    root.title("Music Downloader")
    root.mainloop()
