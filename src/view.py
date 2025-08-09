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

        # Frame principal
        self.main_frame = tk.Frame(root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10)

        # Entradas: Buscar, Canción, Artista (una debajo de otra)
        self.search_label = tk.Label(
            self.main_frame, text="Buscar:", font=("Arial", 12))
        self.search_label.grid(row=0, column=0, sticky="w")
        self.search_entry = tk.Entry(
            self.main_frame, width=30, font=("Arial", 12))
        self.search_entry.grid(row=0, column=1, sticky="w")

        self.song_label = tk.Label(
            self.main_frame, text="Canción:", font=("Arial", 12))
        self.song_label.grid(row=1, column=0, sticky="w")
        self.song_entry = tk.Entry(
            self.main_frame, width=30, font=("Arial", 12))
        self.song_entry.grid(row=1, column=1, sticky="w")

        self.artist_label = tk.Label(
            self.main_frame, text="Artista:", font=("Arial", 12))
        self.artist_label.grid(row=2, column=0, sticky="w")
        self.artist_entry = tk.Entry(
            self.main_frame, width=30, font=("Arial", 12))
        self.artist_entry.grid(row=2, column=1, sticky="w")

        # Botón buscar a la derecha de las entradas
        self.search_button = tk.Button(
            self.main_frame, text="Buscar", font=("Arial", 12), command=self.search_thread)
        self.search_button.grid(
            row=0, column=2, rowspan=3, padx=10, sticky="ns")

        # Holder para la portada debajo
        self.cover_label = tk.Label(
            self.main_frame, text="Portada:", font=("Arial", 12))
        self.cover_label.grid(row=3, column=0, columnspan=4, pady=(10, 0))

        # Labels encima de los listboxes
        self.results_label = tk.Label(
            self.main_frame, text="Resultados de búsqueda:", font=("Arial", 12))
        self.results_label.grid(row=4, column=0, sticky="w", pady=(10, 0))

        self.downloads_label = tk.Label(
            self.main_frame, text="Canciones a descargar:", font=("Arial", 12))
        self.downloads_label.grid(row=4, column=2, sticky="w", pady=(10, 0))

        # Listboxes y formato
        self.results_listbox = tk.Listbox(
            self.main_frame, width=35, height=10, font=("Arial", 12))
        self.results_listbox.grid(row=5, column=0, sticky="w")

        self.results_listbox.bind('<<ListboxSelect>>', self.on_result_select)
        self.results_listbox.bind('<Double-1>', self.add_song)

        self.format_frame = tk.Frame(self.main_frame)
        self.format_frame.grid(row=5, column=1, sticky="n")
        self.format_var = tk.StringVar(value="mp3")
        self.mp3_radio = tk.Radiobutton(
            self.format_frame, text="MP3", variable=self.format_var, value="mp3", font=("Arial", 12))
        self.mp3_radio.pack(anchor="w")
        self.mp4_radio = tk.Radiobutton(
            self.format_frame, text="MP4", variable=self.format_var, value="mp4", font=("Arial", 12))
        self.mp4_radio.pack(anchor="w")

        self.downloads_listbox = tk.Listbox(
            self.main_frame, width=35, height=10, font=("Arial", 12))
        self.downloads_listbox.grid(row=5, column=2, sticky="w")

        self.downloads_listbox.bind('<Double-1>', self.remove_song)

        # Botones agregar, seleccionar todo y eliminar debajo de los listboxes
        self.add_button = tk.Button(self.main_frame, text="Agregar", font=(
            "Arial", 12), command=self.add_song)
        self.add_button.grid(row=6, column=0, pady=10)
        self.select_all_button = tk.Button(self.main_frame, text="Seleccionar todo", font=(
            "Arial", 12), command=self.select_all_results)
        self.select_all_button.grid(row=6, column=1, pady=10)
        self.remove_button = tk.Button(self.main_frame, text="Eliminar", font=(
            "Arial", 12), command=self.remove_song)
        self.remove_button.grid(row=6, column=2, pady=10)

        # Botón descargar debajo
        self.download_button = tk.Button(self.main_frame, text="Descargar", font=(
            "Arial", 12), command=self.download_thread)
        self.download_button.grid(
            row=7, column=0, columnspan=3, pady=10, sticky="ew")

        # Progress bar (oculta al inicio)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=8, column=0, columnspan=3, pady=(10, 0))
        self.progress_bar.grid_remove()

        # Agrega el label de estado al final del constructor
        self.status_label = tk.Label(
            self.main_frame, text="", font=("Arial", 12), fg="blue")
        self.status_label.grid(row=9, column=0, columnspan=3, pady=(5, 0))

    def select_all_results(self):
        for i, result in enumerate(self.controller.last_results):
            format_selected = self.format_var.get()
            format_str = "(MP3)" if format_selected == "mp3" else "(MP4)"
            display_str = f"{format_str} {result.get('artist', '')} - {result.get('title', '')}"
            if display_str not in [song["display"] for song in self.song_list]:
                self.song_list.append({
                    "artist": result.get("artist", ""),
                    "title": result.get("title", ""),
                    "format": format_selected,
                    "display": display_str
                })
                self.downloads_listbox.insert(tk.END, display_str)

    def show_cover(self, image_url):
        try:
            response = requests.get(image_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((120, 120))
            photo = ImageTk.PhotoImage(img)
            self.cover_label.config(image=photo, text="")
            self.cover_label.image = photo  # Mantener referencia
        except Exception:
            self.cover_label.config(image='', text='Sin imagen')

    def on_result_select(self, event):
        selected = self.results_listbox.curselection()
        if selected:
            index = selected[0]
            # Busca el resultado correspondiente en la lista de resultados
            results = self.controller.last_results if hasattr(
                self.controller, 'last_results') else []
            if index < len(results):
                cover_url = results[index].get('cover_url')
                if cover_url:
                    self.show_cover(cover_url)
                else:
                    self.cover_label.config(image='', text='Sin imagen')

    def search_thread(self):
        self.search_button.config(state=tk.DISABLED)
        self.status_label.config(
            text="Obteniendo datos...")  # Muestra el mensaje
        threading.Thread(target=self.search, daemon=True).start()

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
        self.controller.last_results = results
        for i, result in enumerate(results):
            display_artist = result.get('artist', '')
            display_title = result.get('title', '')
            self.results_listbox.insert(
                tk.END, f"{display_artist} - {display_title}")
            if i == 0 and result.get('cover_url'):
                self.show_cover(result['cover_url'])

        self.status_label.config(text="")  # Oculta el mensaje al finalizar
        self.search_button.config(state=tk.NORMAL)

    def add_song(self, event=None):
        selected = self.results_listbox.curselection()
        if selected:
            index = selected[0]
            result = self.controller.last_results[index]
            format_selected = self.format_var.get()
            format_str = "(MP3)" if format_selected == "mp3" else "(MP4)"
            display_str = f"{format_str} {result.get('artist', '')} - {result.get('title', '')}"
            self.song_list.append({
                "artist": result.get("artist", ""),
                "title": result.get("title", ""),
                "format": format_selected,
                "display": display_str
            })
            self.downloads_listbox.insert(tk.END, display_str)
        else:
            messagebox.showerror(
                "Error", "Seleccione una canción de los resultados.")

    def remove_song(self, event=None):
        selected = self.downloads_listbox.curselection()
        if selected:
            index = selected[0]
            self.downloads_listbox.delete(index)
            self.song_list.pop(index)

    def download_thread(self):
        threading.Thread(target=self.start_download).start()

    def start_download(self):
        self.progress_bar.grid()  # Mostrar barra de progreso
        if not hasattr(self, 'save_path') or not self.save_path:
            self.save_path = filedialog.askdirectory()
        if not self.save_path:
            self.progress_bar.grid_remove()
            return
        # Descarga en paralelo
        self.controller.download_multiple_songs(
            self.song_list, self.save_path, self.progress_hook
        )
        messagebox.showinfo("Completado", "Descarga finalizada.")
        self.downloads_listbox.delete(0, tk.END)
        self.song_list.clear()
        self.save_path = None
        self.progress_bar.grid_remove()

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
