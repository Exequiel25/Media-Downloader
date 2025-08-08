import threading
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO


class MusicDownloaderView:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("Descargador de Música y Video")

        self.song_list = []
        self.controller = controller

        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        self.search_label = tk.Label(
            self.frame, text="Buscar:", font=("Arial", 12))
        self.search_label.grid(row=0, column=0)
        self.search_entry = tk.Entry(self.frame, width=30, font=("Arial", 12))
        self.search_entry.grid(row=0, column=1)

        self.search_button = tk.Button(
            self.frame, text="Buscar", font=("Arial", 12), command=self.search)
        self.search_button.grid(row=0, column=2, padx=5)

        self.song_label = tk.Label(
            self.frame, text="Canción:", font=("Arial", 12))
        self.song_label.grid(row=1, column=0)
        self.song_entry = tk.Entry(self.frame, width=30, font=("Arial", 12))
        self.song_entry.grid(row=1, column=1)

        self.artist_label = tk.Label(
            self.frame, text="Artista:", font=("Arial", 12))
        self.artist_label.grid(row=2, column=0)
        self.artist_entry = tk.Entry(self.frame, width=30, font=("Arial", 12))
        self.artist_entry.grid(row=2, column=1)

        self.format_var = tk.StringVar(value="mp3")
        self.format_frame = tk.Frame(root)
        self.format_frame.pack(pady=5)
        tk.Label(self.format_frame, text="Formato:",
                 font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Radiobutton(self.format_frame, text="MP3 (Audio)", variable=self.format_var,
                       value="mp3", font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Radiobutton(self.format_frame, text="MP4 (Video)", variable=self.format_var,
                       value="mp4", font=("Arial", 12)).pack(side=tk.LEFT)

        self.add_button = tk.Button(self.frame, text="Agregar", font=(
            "Arial", 12), command=self.add_song)
        self.add_button.grid(row=3, columnspan=3, pady=5)

        self.cover_label = tk.Label(root, text="Portada:")
        self.cover_label.pack()

        # Listbox de resultados de búsqueda
        self.results_label = tk.Label(root, text="Resultados de búsqueda:")
        self.results_label.pack()
        self.results_listbox = tk.Listbox(
            root, width=50, height=10, font=("Arial", 12))
        self.results_listbox.pack()

        # Listbox de canciones a descargar
        self.downloads_label = tk.Label(root, text="Canciones a descargar:")
        self.downloads_label.pack()
        self.downloads_listbox = tk.Listbox(
            root, width=50, height=10, font=("Arial", 12))
        self.downloads_listbox.pack()

        self.remove_button = tk.Button(root, text="Eliminar", font=(
            "Arial", 12), command=self.remove_song)
        self.remove_button.pack(pady=5)

        self.download_button = tk.Button(root, text="Descargar", font=(
            "Arial", 12), command=self.download_thread)
        self.download_button.pack(pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=5, fill=tk.X)

    def show_cover(self, image_url):
        try:
            response = requests.get(image_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((120, 120))
            photo = ImageTk.PhotoImage(img)
            self.cover_label.config(image=photo)
            self.cover_label.image = photo  # Mantener referencia
        except Exception:
            self.cover_label.config(image='', text='Sin imagen')

    def search(self):
        query = self.search_entry.get().strip()
        artist = self.artist_entry.get().strip()
        title = self.song_entry.get().strip()

        if title:
            if artist:
                results = self.controller.search_by_artist_title(artist, title)
            else:
                results = self.controller.search(title)
        elif query:
            results = self.controller.search(query)
        else:
            messagebox.showerror(
                "Error", "Ingrese un término de búsqueda, canción o artista.")
            return

        self.results_listbox.delete(0, tk.END)
        for i, result in enumerate(results):
            display_artist = result.get('artist', '')
            display_title = result.get('title', '')
            self.results_listbox.insert(
                tk.END, f"{display_artist} - {display_title}")
            if i == 0 and result.get('cover_url'):
                self.show_cover(result['cover_url'])

    def add_song(self):
        selected = self.results_listbox.curselection()
        if selected:
            index = selected[0]
            song_info = self.results_listbox.get(index)
            self.song_list.append(song_info)
            self.downloads_listbox.insert(tk.END, song_info)
        else:
            messagebox.showerror(
                "Error", "Seleccione una canción de los resultados.")

    def remove_song(self):
        selected = self.downloads_listbox.curselection()
        if selected:
            index = selected[0]
            self.downloads_listbox.delete(index)
            self.song_list.pop(index)

    def download_thread(self):
        threading.Thread(target=self.start_download).start()

    def start_download(self):
        if not hasattr(self, 'save_path') or not self.save_path:
            self.save_path = filedialog.askdirectory()
        if not self.save_path:
            return
        format_selected = self.format_var.get()
        for i, song_info in enumerate(self.song_list):
            self.progress_var.set(0)
            try:
                artist, song = song_info.split(" - ", 1)
                self.controller.download_song(
                    song, artist, self.save_path, self.progress_hook, format_selected)
                self.update_listbox(i)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        messagebox.showinfo("Completado", "Descarga finalizada.")
        self.downloads_listbox.delete(0, tk.END)
        self.song_list.clear()
        self.save_path = None

    def progress_hook(self, info):
        if info['status'] == 'downloading':
            total = info.get('total_bytes') or info.get('total_bytes_estimate')
            if total:
                percent = info['downloaded_bytes'] * 100 / total
                self.progress_var.set(percent)
                self.root.update_idletasks()
        elif info['status'] == 'finished':
            self.progress_var.set(100)
            self.root.update_idletasks()

    def update_listbox(self, idx):
        current_text = self.downloads_listbox.get(idx)
        self.downloads_listbox.delete(idx)
        self.downloads_listbox.insert(idx, current_text + " ✔")
