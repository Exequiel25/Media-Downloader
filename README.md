# Music and Video Downloader

This project is a music and video downloader application that allows users to search for songs or videos by song name, artist name, director, actor, or URL. The application features a user-friendly graphical interface and supports downloading content from various sources.

## Project Structure

```
music-video-downloader
├── src
│   ├── view.py          # GUI implementation for the downloader application
│   ├── controller.py    # Application logic and download management
│   ├── model.py         # Data structures for managing song and video information
│   ├── utils
│   │   └── search.py    # Utility functions for searching songs or videos
│   └── types
│       └── index.py     # Type definitions and interfaces used in the application
├── requirements.txt      # List of dependencies required for the project
├── README.md             # Documentation for the project
└── .gitignore            # Files and directories to be ignored by version control
```

## Features

- Search for songs or videos by:
  - Song name
  - Artist name
  - Director
  - Actor
  - URL
- Add and remove songs or videos from the download list
- Progress bar to track download status
- User-friendly interface built with Tkinter

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd music-video-downloader
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

   ```
   python src/view.py
   ```

2. Enter the song or video details in the provided fields.
3. Click "Agregar" to add the item to the download list.
4. Select an item from the list and click "Eliminar" to remove it.
5. Click "Descargar" to start the download process.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
