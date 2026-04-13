# SpotiFilter

A powerful Spotify playlist manager that analyzes your music library and
creates filtered playlists based on specific genres or
countries/regions.

**Author:** Daniel Joy\
**Version:** 1.0.18

------------------------------------------------------------------------

## Table of Contents

-   [Features](#features)
-   [Requirements](#requirements)
-   [Installation](#installation)
-   [Spotify App Setup](#spotify-app-setup)
-   [Configuration](#configuration)
-   [Usage](#usage)
-   [Examples](#examples)
-   [Troubleshooting](#troubleshooting)
-   [Project Structure](#project-structure)
-   [License](#license)

------------------------------------------------------------------------

## Features

- <img src="https://unpkg.com/lucide-static@latest/icons/search.svg" width="16" align="center" style="filter: invert(1);"/> **Library Analysis** – Scan your entire Spotify library, including Liked Songs and personal playlists.
- <img src="https://unpkg.com/lucide-static@latest/icons/music.svg" width="16" align="center" style="filter: invert(1);"/> **Genre Filtering** – Automatically generate playlists for EDM, Rock, Hip-Hop, Jazz, and more.
- <img src="https://unpkg.com/lucide-static@latest/icons/globe.svg" width="16" align="center" style="filter: invert(1);"/> **Regional Filtering** – Create playlists based on origin, such as J-Pop (Japan), K-Pop (Korea), or French Variété.
- <img src="https://unpkg.com/lucide-static@latest/icons/refresh-cw.svg" width="16" align="center" style="filter: invert(1);"/> **Smart Deduplication** – Ensures no duplicate tracks are added, even when scanning multiple sources.
- <img src="https://unpkg.com/lucide-static@latest/icons/list-music.svg" width="16" align="center" style="filter: invert(1);"/> **Playlist Updating** – Seamlessly add new tracks to existing SpotiFilter playlists.
- <img src="https://unpkg.com/lucide-static@latest/icons/lock.svg" width="16" align="center" style="filter: invert(1);"/> **Privacy Control** – Toggle between Public and Private visibility for generated playlists.
- <img src="https://unpkg.com/lucide-static@latest/icons/zap.svg" width="16" align="center" style="filter: invert(1);"/> **Batch Processing** – Optimized API calls to respect Spotify’s rate limits and ensure performance.

------------------------------------------------------------------------

## Requirements

-   **Python 3.7** or higher
-   A **Spotify account** (Free or Premium)
-   **Spotify Developer** credentials (Client ID and Secret)

------------------------------------------------------------------------

## Installation

### 1. Clone the Repository

``` bash
git clone https://github.com/Danieljucke/SpotiFilter.git
cd spotifilter
```

### 2. Install Dependencies

You can install the required packages directly:

``` bash
pip install spotipy python-dotenv
```

Or use the provided `requirements.txt`:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Spotify App Setup

To use SpotiFilter, you must register an application on the Spotify
Developer Portal:

1.  **Visit the Dashboard:** https://developer.spotify.com/dashboard
2.  **Log In:** Use your standard Spotify credentials.
3.  **Create an App:**
    -   **Name:** `SpotiFilter`
    -   **Description:**
        `Playlist generator based on genres and countries.`
    -   **Redirect URI:** `http://127.0.0.1:8000/callback`
4.  **Retrieve Credentials:** Open your app settings to find your
    **Client ID** and **Client Secret**.

------------------------------------------------------------------------

## Configuration

Create a file named `.env` in the root directory:

``` env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

> **IMPORTANT** Never share your `.env` file or commit it to GitHub. It
> is included in the `.gitignore` by default.

------------------------------------------------------------------------

## Usage

### Starting the Application

Run the main script from your terminal:

``` bash
python playlist_generator.py
```

### Workflow

1.  **Source Selection:** Choose whether to scan Liked Songs,
    public/private playlists, or specific selections.
2.  **Analysis:** The script will fetch tracks, remove duplicates, and
    map artists to their respective genres.
3.  **Main Menu:** Select whether you want to filter by **Genre** or
    **Country**.
4.  **Filtering:** Enter your keyword (e.g., `rock`). The script will
    show a preview of matches before creating the playlist.

------------------------------------------------------------------------

## Examples

### Create a "Chill" Genre Playlist

1.  Run the script and select **Option 1** (Liked Songs).
2.  Once analyzed, select **Filter by Genre**.
3.  Enter `chill`.
4.  Confirm creation to generate a new playlist in your Spotify account.

### Update a Regional Playlist

1.  Run the script and select **Option 6** (Scan everything).
2.  Select **Filter by Country**.
3.  Enter `japan`.
4.  If a "Japan Music" playlist already exists, SpotiFilter will only
    add tracks that aren't already there.

------------------------------------------------------------------------

## Troubleshooting

  --------------------------------------------------------------------------
  Issue                               Solution
  ----------------------------------- --------------------------------------
  **ModuleNotFoundError**             Run
                                      `pip install spotipy python-dotenv`.

  **Authentication Error**            Ensure your Redirect URI in the
                                      Dashboard matches
                                      `http://127.0.0.1:8000/callback`.

  **No tracks found**                 Spotify's genres are artist-based. Try
                                      a broader term (e.g., "metal" vs
                                      "technical death metal").

  **Rate Limiting**                   If you have a massive library, wait a
                                      few minutes for the API cool-down
                                      period to end.
  --------------------------------------------------------------------------

------------------------------------------------------------------------

## Project Structure

``` text
spotifilter/
├── playlist_generator.py
├── .env
├── .env.example
├── requirements.txt
└── .gitignore
```

------------------------------------------------------------------------

## Supported Regions (Metadata Mapping)

SpotiFilter looks for specific keywords within Spotify's genre metadata:

-   **Japan:** `j-pop`, `j-rock`, `anime`, `city pop`
-   **Korea:** `k-pop`, `k-rap`, `korean`
-   **France:** `french`, `chanson`
-   **Brazil:** `samba`, `bossa nova`, `mpb`

------------------------------------------------------------------------

## License

This project is for personal use. Please adhere to the Spotify Developer
Terms of Service.

------------------------------------------------------------------------

Enjoy your automated playlists!
