class MusicDownloaderController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.controller = self

    def download_song(self, song, artist, save_path, progress_hook):
        self.model.download_song(song, artist, save_path, progress_hook)
