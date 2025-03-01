import threading
import tkinter as tk
from tkinter import messagebox, filedialog, ttk


class MusicDownloaderView:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Canciones")

        self.song_list = []

        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        self.song_label = tk.Label(
            self.frame, text="Canción:", font=("Arial", 12))
        self.song_label.grid(row=0, column=0)
        self.song_entry = tk.Entry(self.frame, width=30, font=("Arial", 12))
        self.song_entry.grid(row=0, column=1)

        self.artist_label = tk.Label(
            self.frame, text="Artista:", font=("Arial", 12))
        self.artist_label.grid(row=1, column=0)
        self.artist_entry = tk.Entry(self.frame, width=30, font=("Arial", 12))
        self.artist_entry.grid(row=1, column=1)

        self.add_button = tk.Button(self.frame, text="Agregar", font=(
            "Arial", 12), command=self.add_song)
        self.add_button.grid(row=2, columnspan=2, pady=5)

        self.listbox = tk.Listbox(
            root, width=50, height=10, font=("Arial", 12))
        self.listbox.pack()

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

    def add_song(self):
        song = self.song_entry.get()
        artist = self.artist_entry.get()
        if song and artist:
            self.song_list.append((song, artist))
            self.listbox.insert(tk.END, f"{artist} - {song}")
            self.song_entry.delete(0, tk.END)
            self.artist_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Ingrese la canción y el artista.")

    def remove_song(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.listbox.delete(index)
            self.song_list.pop(index)

    def download_thread(self):
        threading.Thread(target=self.start_download).start()

    def start_download(self):
        save_path = filedialog.askdirectory()
        if not save_path:
            return
        for i, (song, artist) in enumerate(self.song_list):
            self.progress_var.set(0)
            try:
                self.controller.download_song(
                    song, artist, save_path, self.progress_hook)
                self.update_listbox(i)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        messagebox.showinfo("Completado", "Descarga finalizada.")
        self.listbox.delete(0, tk.END)
        self.song_list.clear()

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
        current_text = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx, current_text + " ✔")
