"""
SpotiFilter - Spotify Playlist Generator
=======================================
A tool to analyze your Spotify library and create filtered playlists
based on genres, countries/regions, or artists.

Author: Daniel Joy
Version: 2.0.0
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SpotifyPlaylistManager:
    """
    Manages Spotify playlist operations including fetching user data,
    analyzing tracks, filtering by genre/country/artist, and creating/updating playlists.
    """

    def __init__(self):
        """
        Initialize Spotify connection with OAuth authentication.
        
        Required environment variables:
            - SPOTIFY_CLIENT_ID: Your Spotify application client ID
            - SPOTIFY_CLIENT_SECRET: Your Spotify application client secret
        
        Note: You must create a Spotify app at https://developer.spotify.com/dashboard
        and add 'http://127.0.0.1:8000/callback' to the redirect URIs.
        """
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri='http://127.0.0.1:8000/callback',
            scope='playlist-read-private playlist-modify-private playlist-modify-public user-library-read'
        ))
        self.user_id = self.sp.current_user()['id']

    # =========================================================================
    #  DATA FETCHING METHODS
    # =========================================================================

    def get_all_playlists(self):
        """
        Retrieve all playlists owned by the current user (both public and private).
        
        Returns:
            list: A list of playlist objects owned by the user
        """
        playlists = []
        results = self.sp.current_user_playlists(limit=50)

        while results:
            for playlist in results['items']:
                if playlist['owner']['id'] == self.user_id:
                    playlists.append(playlist)
            if results['next']:
                results = self.sp.next(results)
            else:
                break

        return playlists

    def get_liked_songs(self):
        """
        Retrieve all songs from the user's Liked Songs library.
        
        Returns:
            list: A list of saved track objects
        """
        tracks = []
        results = self.sp.current_user_saved_tracks(limit=50)

        print("💚 Fetching Liked Songs...")
        while results:
            tracks.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                break

        print(f"✅ Found {len(tracks)} liked songs")
        return tracks

    def get_playlist_tracks(self, playlist_id):
        """
        Retrieve all tracks from a specific playlist.
        
        Args:
            playlist_id (str): The Spotify ID of the playlist
            
        Returns:
            list: A list of track objects from the playlist
        """
        tracks = []
        results = self.sp.playlist_tracks(playlist_id)

        while results:
            tracks.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                break

        return tracks

    def get_artists_info_batch(self, artist_ids):
        """
        Fetch artist information in batches of 50 (Spotify API limit).
        
        Args:
            artist_ids (list): List of Spotify artist IDs
            
        Returns:
            dict: Mapping of artist_id to {'name': str, 'genres': list}
        """
        artist_map = {}
        unique_ids = list(set(artist_ids))  # Remove duplicates

        for i in range(0, len(unique_ids), 50):
            batch = unique_ids[i:i+50]
            try:
                results = self.sp.artists(batch)
                for artist in results['artists']:
                    if artist:
                        artist_map[artist['id']] = {
                            'name': artist['name'],
                            'genres': artist['genres']
                        }
            except Exception as e:
                print(f"⚠️  Artist batch error: {e}")

        return artist_map

    # =========================================================================
    #  SOURCE SELECTION MENU
    # =========================================================================

    def select_sources(self):
        """
        Display interactive menu for user to select which sources to scan.
        
        Returns:
            tuple: (include_liked (bool), selected_playlists (list))
        """
        print("\n" + "=" * 60)
        print("📂 SOURCE SELECTION")
        print("=" * 60)
        print("1. Liked Songs only")
        print("2. All private playlists")
        print("3. All public playlists")
        print("4. All playlists (public + private)")
        print("5. Select specific playlists")
        print("6. Scan everything (Liked Songs + all playlists)")

        choice = input("\nChoose an option (1-6): ").strip()

        all_playlists = self.get_all_playlists()

        if choice == '1':
            return True, []

        elif choice == '2':
            private = [p for p in all_playlists if not p['public']]
            print(f"✅ {len(private)} private playlists selected")
            return False, private

        elif choice == '3':
            public = [p for p in all_playlists if p['public']]
            print(f"✅ {len(public)} public playlists selected")
            return False, public

        elif choice == '4':
            print(f"✅ {len(all_playlists)} playlists selected")
            return False, all_playlists

        elif choice == '5':
            return self._manual_playlist_selection(all_playlists)

        elif choice == '6':
            print(f"✅ Liked Songs + {len(all_playlists)} playlists selected")
            return True, all_playlists

        else:
            print("❌ Invalid option, defaulting to full scan")
            return True, all_playlists

    def _manual_playlist_selection(self, all_playlists):
        """
        Display list of playlists and allow user to select multiple by number.
        
        Args:
            all_playlists (list): List of all user's playlists
            
        Returns:
            tuple: (include_liked (bool), selected_playlists (list))
        """
        print("\n📋 Your available playlists:")
        print(f"  {'No.':<5} {'Visibility':<14} {'Tracks':<8} Name")
        print("  " + "-" * 55)
        print(f"  {'0':<5} {'♥ special':<14} {'':8} Liked Songs")

        for i, p in enumerate(all_playlists, start=1):
            visibility = "🔓 public" if p['public'] else "🔒 private"
            track_count = p['tracks']['total']
            print(f"  {str(i):<5} {visibility:<14} {str(track_count):<8} {p['name']}")

        print("\nEnter numbers separated by commas (e.g., 0,2,5)")
        raw = input("Your selection: ").strip()

        selected_playlists = []
        include_liked = False

        try:
            indices = [int(x.strip()) for x in raw.split(',') if x.strip()]
        except ValueError:
            print("❌ Invalid input, defaulting to full scan")
            return True, all_playlists

        for idx in indices:
            if idx == 0:
                include_liked = True
            elif 1 <= idx <= len(all_playlists):
                selected_playlists.append(all_playlists[idx - 1])
            else:
                print(f"⚠️  Number {idx} ignored (out of range)")

        liked_label = " + Liked Songs" if include_liked else ""
        print(f"✅ {len(selected_playlists)} playlist(s){liked_label} selected")
        return include_liked, selected_playlists

    # =========================================================================
    #  TRACK ANALYSIS
    # =========================================================================

    def analyze_tracks(self, include_liked, playlists):
        """
        Analyze tracks from selected sources.
        
        Process:
            1. Collect all tracks from selected sources (deduplicated)
            2. Fetch artist information in batches (1 API call per 50 artists)
            3. Assemble final data structure with track and artist info
        
        Args:
            include_liked (bool): Whether to include Liked Songs
            playlists (list): List of playlist objects to analyze
            
        Returns:
            dict: Mapping of track_id to {
                'name': str,
                'uri': str,
                'artists': [{'name': str, 'genres': list}, ...]
            }
        """
        # Step 1: Collect raw track data
        raw_tracks = {}  # track_id -> {name, uri, artist_ids: []}

        def collect_track(track):
            """Helper to add track to raw_tracks collection."""
            if not track or not track.get('id'):
                return
            track_id = track['id']
            if track_id in raw_tracks:
                return
            raw_tracks[track_id] = {
                'name': track['name'],
                'uri': track['uri'],
                'artist_ids': [a['id'] for a in track['artists'] if a.get('id')],
                'artist_names': [a['name'] for a in track['artists'] if a.get('name')]
            }

        if include_liked:
            liked_tracks = self.get_liked_songs()
            for item in liked_tracks:
                collect_track(item.get('track'))
            print()

        for playlist in playlists:
            print(f"📝 Collecting: {playlist['name']} ({playlist['tracks']['total']} tracks)")
            tracks = self.get_playlist_tracks(playlist['id'])
            for item in tracks:
                collect_track(item.get('track'))

        # Step 2: Fetch all artist information in batches
        all_artist_ids = {aid for t in raw_tracks.values() for aid in t['artist_ids']}
        total_batches = (len(all_artist_ids) + 49) // 50
        print(f"\n🎤 Fetching genres for {len(all_artist_ids)} artists "
              f"({total_batches} request(s))...")

        artist_map = self.get_artists_info_batch(list(all_artist_ids))

        # Step 3: Assemble final result
        track_artists_map = {}
        for track_id, t in raw_tracks.items():
            track_artists_map[track_id] = {
                'name': t['name'],
                'uri': t['uri'],
                'artist_names': t['artist_names'],
                'artists': []
            }
            for aid in t['artist_ids']:
                info = artist_map.get(aid, {'name': 'Unknown', 'genres': []})
                track_artists_map[track_id]['artists'].append(info)

        print(f"✅ {len(track_artists_map)} unique songs analyzed (duplicates removed)\n")
        return track_artists_map

    # =========================================================================
    #  FILTERING METHODS
    # =========================================================================

    def filter_by_genre(self, tracks_map, genre_keyword):
        """
        Filter tracks by genre keyword.
        
        Args:
            tracks_map (dict): The analyzed tracks mapping from analyze_tracks()
            genre_keyword (str): Genre to search for (e.g., 'amapiano', 'afrobeats')
            
        Returns:
            list: Filtered tracks with format:
                [{'uri': str, 'name': str, 'artist': str, 'genres': list}, ...]
        """
        filtered_tracks = []
        genre_keyword = genre_keyword.lower()
        seen_track_ids = set()

        for track_id, track_info in tracks_map.items():
            for artist in track_info['artists']:
                if any(genre_keyword in genre.lower() for genre in artist['genres']):
                    if track_id not in seen_track_ids:
                        filtered_tracks.append({
                            'uri': track_info['uri'],
                            'name': track_info['name'],
                            'artist': artist['name'],
                            'genres': artist['genres']
                        })
                        seen_track_ids.add(track_id)
                    break

        return filtered_tracks

    def filter_by_country(self, tracks_map, country_keyword):
        """
        Filter tracks by country/region based on genre associations.
        
        Args:
            tracks_map (dict): The analyzed tracks mapping from analyze_tracks()
            country_keyword (str): Country/region to search for
            
        Returns:
            list: Filtered tracks with format:
                [{'uri': str, 'name': str, 'artist': str, 'genres': list}, ...]
        """
        country_keywords = {

            # == AFRICA ========================================================
            # Pan-African / Afro umbrella
            'africa':           ['afrobeats', 'afropop', 'afro pop', 'afroswing',
                                 'afro swing', 'afro soul', 'afrofusion', 'afro fusion',
                                 'afro house', 'afro dancehall', 'afrorave',
                                 'afrobeat',  # Fela Kuti classic tag
                                 'african'],
            'african':          ['afrobeats', 'afropop', 'afro pop', 'afroswing',
                                 'afro swing', 'afro soul', 'afrofusion', 'afro fusion',
                                 'afro house', 'afro dancehall', 'afrorave',
                                 'afrobeat', 'african'],

            # Nigeria
            'nigeria':          ['afrobeats', 'afropop', 'afro pop', 'naija',
                                 'nigerian', 'afrorave', 'afrofusion', 'afro fusion',
                                 'highlife', 'afroswing', 'afrobeat'],
            'nigerian':         ['afrobeats', 'afropop', 'afro pop', 'naija',
                                 'nigerian', 'afrorave', 'afrofusion', 'afro fusion',
                                 'highlife', 'afroswing', 'afrobeat'],

            # South Africa
            'south africa':     ['amapiano', 'gqom', 'afro house', 'kwaito',
                                 'south african', 'sa hip hop', 'maskandi',
                                 'bubblegum', 'afropop'],
            'south african':    ['amapiano', 'gqom', 'afro house', 'kwaito',
                                 'south african', 'sa hip hop', 'maskandi',
                                 'bubblegum', 'afropop'],
            'amapiano':         ['amapiano'],
            'gqom':             ['gqom'],

            # Ghana
            'ghana':            ['highlife', 'hiplife', 'azonto', 'ghanaian',
                                 'afrobeats', 'afropop'],
            'ghanaian':         ['highlife', 'hiplife', 'azonto', 'ghanaian',
                                 'afrobeats', 'afropop'],

            # Tanzania / East Africa
            'tanzania':         ['bongo flava', 'bongo', 'tanzanian', 'east african'],
            'east africa':      ['bongo flava', 'afropop', 'benga', 'taarab',
                                 'east african'],

            # Kenya
            'kenya':            ['kenyan', 'genge', 'benga', 'afropop', 'east african'],
            'kenyan':           ['kenyan', 'genge', 'benga', 'afropop', 'east african'],

            # Senegal / West Africa
            'senegal':          ['mbalax', 'senegalese', 'wolof', 'west african'],
            'west africa':      ['mbalax', 'afrobeats', 'afropop', 'highlife',
                                 'palm wine', 'west african'],

            # Cameroon
            'cameroon':         ['bikutsi', 'makossa', 'cameroonian', 'afropop'],
            'cameroonian':      ['bikutsi', 'makossa', 'cameroonian', 'afropop'],

            # Congo / DRC
            'congo':            ['soukous', 'congolese', 'rumba', 'ndombolo',
                                 'afro rumba'],
            'congolese':        ['soukous', 'congolese', 'rumba', 'ndombolo',
                                 'afro rumba'],

            # Ethiopia
            'ethiopia':         ['ethiopian', 'ethio jazz', 'afropop'],
            'ethiopian':        ['ethiopian', 'ethio jazz', 'afropop'],

            # Zimbabwe / Southern Africa
            'zimbabwe':         ['zimbabwean', 'chimurenga', 'afropop'],
            'southern africa':  ['amapiano', 'kwaito', 'gqom', 'afro house',
                                 'chimurenga', 'mbaqanga'],

            # North Africa / Maghreb
            'north africa':     ['rai', 'chaabi', 'gnawa', 'shaabi', 'arabic',
                                 'moroccan', 'algerian', 'tunisian', 'north african'],
            'morocco':          ['moroccan', 'gnawa', 'chaabi', 'rai', 'amazigh'],
            'moroccan':         ['moroccan', 'gnawa', 'chaabi', 'rai', 'amazigh'],
            'algeria':          ['algerian', 'rai', 'chaabi', 'kabyle'],
            'algerian':         ['algerian', 'rai', 'chaabi', 'kabyle'],
            'egypt':            ['egyptian', 'shaabi', 'arabic pop', 'arabic'],
            'egyptian':         ['egyptian', 'shaabi', 'arabic pop', 'arabic'],

            # == ASIA ==========================================================
            # Japan
            'japan':            ['j-pop', 'j-rock', 'japanese', 'anime', 'city pop',
                                 'j-hip hop', 'j-indie', 'visual kei', 'enka', 'shibuya-kei'],
            'japanese':         ['j-pop', 'j-rock', 'japanese', 'anime', 'city pop',
                                 'j-hip hop', 'j-indie', 'visual kei', 'enka', 'shibuya-kei'],

            # South Korea
            'korea':            ['k-pop', 'k-rap', 'korean', 'k-indie', 'k-hip hop',
                                 'k-rnb', 'trot'],
            'korean':           ['k-pop', 'k-rap', 'korean', 'k-indie', 'k-hip hop',
                                 'k-rnb', 'trot'],

            # India
            'india':            ['bollywood', 'indian', 'hindi', 'punjabi', 'bhangra',
                                 'carnatic', 'hindustani', 'filmi', 'desi', 'kollywood',
                                 'tollywood', 'tamil', 'telugu', 'malayalam'],
            'indian':           ['bollywood', 'indian', 'hindi', 'punjabi', 'bhangra',
                                 'carnatic', 'hindustani', 'filmi', 'desi', 'kollywood',
                                 'tollywood', 'tamil', 'telugu', 'malayalam'],

            # Pakistan
            'pakistan':         ['pakistani', 'punjabi', 'qawwali', 'ghazal',
                                 'sufi', 'desi'],
            'pakistani':        ['pakistani', 'punjabi', 'qawwali', 'ghazal',
                                 'sufi', 'desi'],

            # China
            'china':            ['chinese', 'mandopop', 'c-pop', 'cantopop',
                                 'chinese classical'],
            'chinese':          ['chinese', 'mandopop', 'c-pop', 'cantopop'],

            # Philippines
            'philippines':      ['opm', 'filipino', 'p-pop', 'philippine'],
            'filipino':         ['opm', 'filipino', 'p-pop', 'philippine'],

            # Indonesia
            'indonesia':        ['indonesian', 'dangdut', 'pop indonesia'],
            'indonesian':       ['indonesian', 'dangdut', 'pop indonesia'],

            # Thailand
            'thailand':         ['thai', 't-pop', 'luk thung', 'mor lam'],
            'thai':             ['thai', 't-pop', 'luk thung', 'mor lam'],

            # Vietnam
            'vietnam':          ['v-pop', 'vietnamese', 'bolero vietnam'],
            'vietnamese':       ['v-pop', 'vietnamese'],

            # Turkey
            'turkey':           ['turkish', 'arabesk', 'halk muzigi', 'turkish pop'],
            'turkish':          ['turkish', 'arabesk', 'halk muzigi', 'turkish pop'],

            # Iran
            'iran':             ['iranian', 'persian', 'persian pop'],
            'iranian':          ['iranian', 'persian', 'persian pop'],
            'persian':          ['persian', 'iranian', 'persian pop'],

            # == MIDDLE EAST ===================================================
            'middle east':      ['arabic', 'khaleeji', 'levantine', 'arabic pop',
                                 'arabic hip hop', 'gulf', 'middle eastern'],
            'arabic':           ['arabic', 'arabic pop', 'arabic hip hop', 'khaleeji',
                                 'levantine', 'gulf'],
            'saudi arabia':     ['khaleeji', 'arabic', 'arabic pop', 'gulf'],
            'gulf':             ['khaleeji', 'gulf', 'arabic pop'],
            'lebanon':          ['lebanese', 'arabic pop', 'levantine'],
            'lebanese':         ['lebanese', 'arabic pop', 'levantine'],

            # == EUROPE ========================================================
            # UK
            'uk':               ['british', 'uk', 'garage', 'uk garage', 'grime',
                                 'drum and bass', 'dnb', 'afroswing', 'uk drill',
                                 'britpop', 'uk hip hop'],
            'british':          ['british', 'uk', 'garage', 'uk garage', 'grime',
                                 'drum and bass', 'dnb', 'afroswing', 'uk drill',
                                 'britpop', 'uk hip hop'],

            # France
            'france':           ['french', 'chanson', 'variete', 'french pop',
                                 'french hip hop', 'french house', 'electro francais'],
            'french':           ['french', 'chanson', 'variete', 'french pop',
                                 'french hip hop', 'french house', 'electro francais'],

            # Germany
            'germany':          ['german', 'deutsch', 'schlager', 'neue deutsche welle',
                                 'krautrock', 'german hip hop', 'techno'],
            'german':           ['german', 'deutsch', 'schlager', 'neue deutsche welle',
                                 'krautrock', 'german hip hop', 'techno'],

            # Spain
            'spain':            ['spanish', 'flamenco', 'latin', 'reggaeton espanol',
                                 'rumba catalana', 'spanish pop'],
            'spanish':          ['spanish', 'flamenco', 'latin', 'reggaeton espanol',
                                 'rumba catalana', 'spanish pop'],

            # Italy
            'italy':            ['italian', 'canzone', 'italo disco', 'italian pop',
                                 'opera', 'italian hip hop'],
            'italian':          ['italian', 'canzone', 'italo disco', 'italian pop',
                                 'opera', 'italian hip hop'],

            # Portugal
            'portugal':         ['fado', 'portuguese', 'pimba', 'portuguese pop'],
            'portuguese':       ['fado', 'portuguese', 'pimba', 'portuguese pop'],

            # Netherlands
            'netherlands':      ['dutch', 'nederlandstalig', 'dutch pop', 'dutch hip hop'],
            'dutch':            ['dutch', 'nederlandstalig', 'dutch pop', 'dutch hip hop'],

            # Scandinavia
            'scandinavia':      ['scandinavian', 'nordic', 'swedish', 'norwegian',
                                 'danish', 'finnish'],
            'sweden':           ['swedish', 'swedish pop', 'scandinavian'],
            'swedish':          ['swedish', 'swedish pop', 'scandinavian'],
            'norway':           ['norwegian', 'scandinavian'],
            'norwegian':        ['norwegian', 'scandinavian'],
            'denmark':          ['danish', 'scandinavian'],
            'danish':           ['danish', 'scandinavian'],
            'finland':          ['finnish', 'suomi pop', 'scandinavian'],
            'finnish':          ['finnish', 'suomi pop', 'scandinavian'],

            # Russia
            'russia':           ['russian', 'russki', 'russian pop'],
            'russian':          ['russian', 'russki', 'russian pop'],

            # Eastern Europe
            'eastern europe':   ['balkan', 'slavic', 'romanian', 'bulgarian',
                                 'serbian', 'polish', 'czech', 'hungarian'],
            'balkans':          ['balkan', 'turbofolk', 'serbian', 'balkan brass',
                                 'gypsy'],
            'romania':          ['romanian', 'manele'],
            'romanian':         ['romanian', 'manele'],
            'poland':           ['polish', 'polski rap'],
            'polish':           ['polish', 'polski rap'],
            'greece':           ['greek', 'laiko', 'rebetiko', 'entechno'],
            'greek':            ['greek', 'laiko', 'rebetiko', 'entechno'],

            # == AMERICAS =====================================================
            # USA
            'usa':              ['american'],
            'american':         ['american'],

            # Brazil
            'brazil':           ['brazilian', 'samba', 'bossa nova', 'mpb',
                                 'funk carioca', 'funk brasileiro', 'pagode',
                                 'axe', 'forro', 'sertanejo', 'baile funk',
                                 'tropicalia'],
            'brazilian':        ['brazilian', 'samba', 'bossa nova', 'mpb',
                                 'funk carioca', 'funk brasileiro', 'pagode',
                                 'axe', 'forro', 'sertanejo', 'baile funk',
                                 'tropicalia'],

            # Colombia
            'colombia':         ['colombian', 'cumbia', 'vallenato', 'currulao',
                                 'mapalé', 'latin'],
            'colombian':        ['colombian', 'cumbia', 'vallenato', 'latin'],

            # Mexico
            'mexico':           ['mexican', 'mariachi', 'ranchera', 'banda',
                                 'norteño', 'corrido', 'cumbia', 'latin'],
            'mexican':          ['mexican', 'mariachi', 'ranchera', 'banda',
                                 'norteño', 'corrido', 'cumbia', 'latin'],

            # Argentina
            'argentina':        ['argentinian', 'tango', 'folklore argentino',
                                 'cumbia villera', 'latin'],
            'argentinian':      ['argentinian', 'tango', 'folklore argentino', 'latin'],

            # Cuba
            'cuba':             ['cuban', 'salsa', 'son cubano', 'mambo', 'bolero',
                                 'timba', 'rumba cubana'],
            'cuban':            ['cuban', 'salsa', 'son cubano', 'mambo', 'bolero',
                                 'timba', 'rumba cubana'],

            # Puerto Rico / Reggaeton
            'puerto rico':      ['reggaeton', 'latin trap', 'dembow', 'latin urban',
                                 'puerto rican', 'salsa'],
            'reggaeton':        ['reggaeton', 'latin trap', 'dembow', 'latin urban'],

            # Dominican Republic
            'dominican republic': ['bachata', 'merengue', 'dominican', 'dembow'],
            'dominican':        ['bachata', 'merengue', 'dominican', 'dembow'],

            # Jamaica
            'jamaica':          ['reggae', 'dancehall', 'ska', 'rocksteady',
                                 'jamaican', 'dub'],
            'jamaican':         ['reggae', 'dancehall', 'ska', 'rocksteady',
                                 'jamaican', 'dub'],

            # Trinidad
            'trinidad':         ['soca', 'calypso', 'trinidadian', 'chutney'],
            'trinidadian':      ['soca', 'calypso', 'trinidadian', 'chutney'],

            # Chile
            'chile':            ['chilean', 'cueca', 'latin'],
            'chilean':          ['chilean', 'cueca', 'latin'],

            # Peru
            'peru':             ['peruvian', 'cumbia peruana', 'chicha', 'latin'],
            'peruvian':         ['peruvian', 'cumbia peruana', 'chicha', 'latin'],

            # == OCEANIA =======================================================
            'australia':        ['australian', 'australian hip hop', 'oz hip hop'],
            'australian':       ['australian', 'australian hip hop', 'oz hip hop'],
        }

        search_terms = country_keywords.get(country_keyword.lower(), [country_keyword.lower()])
        filtered_tracks = []
        seen_track_ids = set()

        for track_id, track_info in tracks_map.items():
            for artist in track_info['artists']:
                if any(any(term in genre.lower() for term in search_terms)
                       for genre in artist['genres']):
                    if track_id not in seen_track_ids:
                        filtered_tracks.append({
                            'uri': track_info['uri'],
                            'name': track_info['name'],
                            'artist': artist['name'],
                            'genres': artist['genres']
                        })
                        seen_track_ids.add(track_id)
                    break

        return filtered_tracks

    def filter_by_artist(self, tracks_map, artist_keyword):
        """
        Filter tracks by artist name (case-insensitive partial match).
        
        Args:
            tracks_map (dict): The analyzed tracks mapping from analyze_tracks()
            artist_keyword (str): Artist name (or partial name) to search for
            
        Returns:
            list: Filtered tracks with format:
                [{'uri': str, 'name': str, 'artist': str, 'genres': list}, ...]
        """
        filtered_tracks = []
        artist_keyword = artist_keyword.lower()
        seen_track_ids = set()

        for track_id, track_info in tracks_map.items():
            for artist in track_info['artists']:
                if artist_keyword in artist['name'].lower():
                    if track_id not in seen_track_ids:
                        filtered_tracks.append({
                            'uri': track_info['uri'],
                            'name': track_info['name'],
                            'artist': artist['name'],
                            'genres': artist['genres']
                        })
                        seen_track_ids.add(track_id)
                    break

        return filtered_tracks

    # =========================================================================
    #  PLAYLIST CREATION AND UPDATE
    # =========================================================================

    def find_existing_playlist(self, playlist_name):
        """
        Check if a playlist with the given name already exists for the user.
        
        Args:
            playlist_name (str): Name of the playlist to search for
            
        Returns:
            dict or None: Playlist object if found, None otherwise
        """
        results = self.sp.current_user_playlists(limit=50)

        while results:
            for playlist in results['items']:
                if (playlist['owner']['id'] == self.user_id and
                        playlist['name'].lower() == playlist_name.lower()):
                    return playlist
            if results['next']:
                results = self.sp.next(results)
            else:
                break

        return None

    def get_existing_playlist_tracks(self, playlist_id):
        """
        Retrieve URIs of all tracks currently in a playlist.
        
        Args:
            playlist_id (str): Spotify ID of the playlist
            
        Returns:
            set: Set of track URIs already in the playlist
        """
        existing_uris = set()
        results = self.sp.playlist_tracks(playlist_id)

        while results:
            for item in results['items']:
                if item.get('track') and item['track'].get('uri'):
                    existing_uris.add(item['track']['uri'])
            if results.get('next'):
                results = self.sp.next(results)
            else:
                break

        return existing_uris

    def ask_visibility(self):
        """
        Prompt user for playlist visibility preference.
        
        Returns:
            bool: True for public, False for private
        """
        while True:
            response = input("Should the playlist be (p)ublic or (pr)ivate? [pr default]: ").strip().lower()
            if response in ('p', 'public'):
                return True
            elif response in ('', 'pr', 'private'):
                return False
            else:
                print("❌ Please answer 'p' for public or 'pr' for private.")

    def create_or_update_playlist(self, name, description, track_uris, is_public=False):
        """
        Create a new playlist or update an existing one with new tracks.
        
        Args:
            name (str): Playlist name
            description (str): Playlist description
            track_uris (list): List of Spotify track URIs to add
            is_public (bool): Whether the playlist should be public
            
        Returns:
            dict or None: Playlist object if successful, None otherwise
        """
        if not track_uris:
            print("❌ No tracks found to create playlist")
            return None

        existing_playlist = self.find_existing_playlist(name)

        if existing_playlist:
            print(f"\n📋 Playlist '{name}' already exists!")
            playlist_id = existing_playlist['id']

            try:
                existing_uris = self.get_existing_playlist_tracks(playlist_id)
            except Exception as e:
                print(f"❌ Error fetching existing tracks: {e}")
                return None

            new_uris = [uri for uri in track_uris if uri not in existing_uris]

            if new_uris:
                print(f"➕ Adding {len(new_uris)} new tracks (out of {len(track_uris)} total)")
                try:
                    for i in range(0, len(new_uris), 100):
                        self.sp.playlist_add_items(playlist_id, new_uris[i:i+100])
                    print(f"✅ Playlist updated! Total: {len(existing_uris) + len(new_uris)} tracks")
                except Exception as e:
                    print(f"❌ Error adding tracks: {e}")
                    return None
            else:
                print("ℹ️  No new tracks to add (all already present)")

            print(f"🔗 Link: {existing_playlist['external_urls']['spotify']}")
            return existing_playlist

        else:
            try:
                playlist = self.sp.user_playlist_create(
                    user=self.user_id,
                    name=name,
                    public=is_public,
                    description=description
                )
                for i in range(0, len(track_uris), 100):
                    self.sp.playlist_add_items(playlist['id'], track_uris[i:i+100])

                visibility_label = "public" if is_public else "private"
                print(f"✅ New playlist '{name}' created ({visibility_label}) with {len(track_uris)} tracks!")
                print(f"🔗 Link: {playlist['external_urls']['spotify']}")
                return playlist
            except Exception as e:
                print(f"❌ Error creating playlist: {e}")
                return None


# =============================================================================
#  HELPER FUNCTIONS
# =============================================================================

def handle_filter_result(manager, filtered_tracks, filter_label, default_name):
    """
    Common logic after filtering: show preview and handle playlist creation/update.
    
    Args:
        manager (SpotifyPlaylistManager): The playlist manager instance
        filtered_tracks (list): List of filtered track objects
        filter_label (str): Label describing the filter (genre, country, or artist)
        default_name (str): Default name for the playlist
    """
    if not filtered_tracks:
        print(f"❌ No tracks found for '{filter_label}'")
        return

    print(f"\n✅ Found {len(filtered_tracks)} unique tracks for '{filter_label}'")
    print("\nPreview (first 10 tracks):")
    for i, track in enumerate(filtered_tracks[:10], 1):
        print(f"{i}. {track['name']} - {track['artist']}")
        print(f"   Genres: {', '.join(track['genres'][:3])}")

    create = input(f"\nCreate/Update playlist '{default_name}'? (y/n): ").lower()
    if create != 'y':
        return

    playlist_name = input("Playlist name (or Enter for default): ").strip()
    if not playlist_name:
        playlist_name = default_name

    existing = manager.find_existing_playlist(playlist_name)
    is_public = False
    if not existing:
        is_public = manager.ask_visibility()

    uris = [t['uri'] for t in filtered_tracks]
    manager.create_or_update_playlist(
        name=playlist_name,
        description=f"Auto-generated playlist - {filter_label}",
        track_uris=uris,
        is_public=is_public
    )


# =============================================================================
#  MAIN PROGRAM
# =============================================================================

def main():
    """Main entry point for the SpotiFilter application."""
    print("=" * 60)
    print("🎵 SPOTIFILTER - SPOTIFY PLAYLIST MANAGER 🎵")
    print("=" * 60)
    print("\n⚠️  Make sure you have configured your Spotify credentials:")
    print("   - SPOTIFY_CLIENT_ID")
    print("   - SPOTIFY_CLIENT_SECRET")
    print("   Create an app at: https://developer.spotify.com/dashboard")
    print("   Add 'http://127.0.0.1:8000/callback' to redirect URIs\n")

    try:
        manager = SpotifyPlaylistManager()

        # Source selection
        include_liked, selected_playlists = manager.select_sources()

        if not include_liked and not selected_playlists:
            print("❌ No sources selected. Exiting.")
            return

        # Analyze tracks
        tracks_map = manager.analyze_tracks(include_liked, selected_playlists)

        if not tracks_map:
            print("❌ No tracks found in selected sources.")
            return

        # Main menu loop
        while True:
            print("\n" + "=" * 60)
            print("MAIN MENU")
            print("=" * 60)
            print("1. Filter by GENRE")
            print("   (e.g., amapiano, afrobeats, afropop, gqom, afro house,")
            print("    kwaito, afroswing, highlife, edm, rock, hip-hop, jazz)")
            print("2. Filter by COUNTRY/REGION")
            print("   (e.g., nigeria, south africa, ghana, kenya, morocco,")
            print("    japan, korea, france, brazil, colombia, jamaica)")
            print("3. Filter by ARTIST")
            print("   (e.g., Burna Boy, Wizkid, Davido, Asake, Rema)")
            print("4. Change analyzed sources")
            print("5. Exit")

            choice = input("\nChoose an option (1-5): ").strip()

            if choice == '1':
                print("\n🎵 Afro genres: amapiano, afrobeats, afropop, gqom, afro house,")
                print("               kwaito, highlife, afroswing, bongo flava, afrofusion")
                print("🎵 Other genres: edm, rock, pop, hip-hop, jazz, metal, indie, r&b,")
                print("               reggaeton, dancehall, samba, cumbia, classical")
                genre = input("\nEnter genre to search for: ").strip()
                if not genre:
                    print("❌ Invalid genre")
                    continue
                filtered = manager.filter_by_genre(tracks_map, genre)
                handle_filter_result(manager, filtered, genre, f"{genre.upper()} Mix")

            elif choice == '2':
                print("\n🌍 Africa:   nigeria, south africa, ghana, kenya, tanzania,")
                print("             senegal, congo, ethiopia, morocco, egypt")
                print("🌍 Asia:     japan, korea, india, china, philippines, indonesia")
                print("🌍 Americas: brazil, colombia, mexico, jamaica, puerto rico")
                print("🌍 Europe:   france, uk, germany, spain, italy, portugal")
                print("🌍 Middle East: arabic, lebanon, gulf")
                country = input("\nEnter country/region to search for: ").strip()
                if not country:
                    print("❌ Invalid country")
                    continue
                filtered = manager.filter_by_country(tracks_map, country)
                handle_filter_result(manager, filtered, country, f"{country.title()} Music")

            elif choice == '3':
                artist = input("\n🎤 Enter artist name (or partial name): ").strip()
                if not artist:
                    print("❌ Invalid artist name")
                    continue
                filtered = manager.filter_by_artist(tracks_map, artist)
                handle_filter_result(manager, filtered, artist, f"{artist.title()} Collection")

            elif choice == '4':
                include_liked, selected_playlists = manager.select_sources()
                if not include_liked and not selected_playlists:
                    print("❌ No sources selected.")
                    continue
                tracks_map = manager.analyze_tracks(include_liked, selected_playlists)
                if not tracks_map:
                    print("❌ No tracks found in selected sources.")

            elif choice == '5':
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid option")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease verify:")
        print("1. Your Spotify credentials are correct")
        print("2. You have installed spotipy: pip install spotipy")
        print("3. You have installed python-dotenv: pip install python-dotenv")
        print("4. You have authorized the application on first connection")


if __name__ == "__main__":
    main()