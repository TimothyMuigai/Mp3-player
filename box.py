from tkinter import *
from tkinter import ttk
from tkinter import filedialog, Listbox
from tkinter import messagebox, Toplevel
import pygame, yt_dlp, threading
import os, time, random, requests,re
from mutagen.mp3 import MP3
from tkinter.filedialog import asksaveasfilename
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Spotify Authentication
sp_oauth = SpotifyOAuth(
    client_id=YOUR_APP_CLIENT_ID,
    client_secret=YOUR_APP_CLIENT_SECRET,
    redirect_uri=YOUR_APP_REDIRECT_URI,
    scope="playlist-modify-public playlist-modify-private playlist-read-private",
    cache_path=".spotify_cache"  # Stores the token so it refreshes automatically
)

def get_spotify_client():
    """Ensures Spotify authentication and refreshes token automatically."""
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        print("🔴 No cached token found. Opening authentication URL...")
        auth_url = sp_oauth.get_authorize_url()
        print(f"🔗 Please authorize the app by visiting: {auth_url}")
        
        import webbrowser
        webbrowser.open(auth_url)  # Opens the auth page in the browser automatically
        
        response = input("🔑 After authorizing, paste the redirected URL here: ").strip()
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code, as_dict=True)

    # Refresh token if expired
    if sp_oauth.is_token_expired(token_info):
        print("🔄 Refreshing Spotify token...")
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    # Return authenticated Spotify client
    return spotipy.Spotify(auth=token_info["access_token"])

# Create Spotify Client
sp = get_spotify_client()

# listbox functions
def get_authenticated_service():
    """Handles OAuth authentication, storing and using refresh tokens."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE)

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # Refresh token automatically
            else:
                raise Exception("Refresh token missing or invalid")

        except Exception as e:
            print("🔄 Refresh token expired or missing. Re-authenticating...")

            # Request new authentication
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=8080, access_type="offline", prompt="consent")

        # Save new credentials
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds

# Authenticate and create YouTube API client
creds = get_authenticated_service()
youtube = build("youtube", "v3", credentials=creds)

def get_user_details():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id= YOUR_APP_CLIENT_ID,
            client_secret= YOUR_APP_CLIENT_SECRET,
            redirect_uri= YOUR_APP_REDIRECT_URI,
            scope='playlist-modify-public'
        )
    )

    user_info = sp.current_user()
    return user_info
window = Tk()
# width x height
window.geometry('1200x900')
# main container details
heading = Label(
    window,
    text='Music player',
    font=("Helvetica", 14)
)
heading.pack()
    # added a notebook to hold all pages 
main_tab = ttk.Notebook(
    window,
)
main_tab.pack(pady=5,fill=X)

# ✅tab one in the notebook to hold other components
tab1 = Frame(
    main_tab
)
pygame.mixer.init()

tab1.grid_rowconfigure(0, weight=2)
tab1.grid_columnconfigure(0, weight=1)

# ✅frame 1 in tab one
frame1 = Frame(
    tab1,
    width=800,
    height=500,
    bg='blue'
)
frame1.grid(row=0, column=0, padx=50, pady=5,sticky="nsew")
frame1.grid_propagate(False)

songs = []
current_song = ""
paused = False

def load_music():
    global current_song
    new_directory = filedialog.askdirectory()

    if not new_directory:
        return

    tab1.directory = new_directory
    new_songs = []

    for song in os.listdir(tab1.directory):
        name, ext = os.path.splitext(song)
        if ext == '.mp3':
            new_songs.append(song)

    if new_songs:
        songs.clear()
        songs.extend(new_songs)
        listbox_item.delete(0, END) 

        for song in songs:
            listbox_item.insert('end', song)
        
        listbox_item.select_set(0)
        current_song = songs[listbox_item.curselection()[0]]


def startup():
    tab1.directory = r'C:\Users\user\Music\python-test'    

    for song in os.listdir(tab1.directory):
        name,ext = os.path.splitext(song)
        if ext == '.mp3':
            songs.append(song)

    if songs:
        for song in songs:
            listbox_item.insert('end', song)
        listbox_item.select_set(0)
        current_song = songs[listbox_item.curselection()[0]]
def delete_selected_song():
    global current_song

    try:
        # Get the selected song
        selected_index = listbox_item.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "No song selected!")
            return

        song_to_delete = songs[selected_index[0]]
        file_path = os.path.join(tab1.directory, song_to_delete)

        # Confirm before deleting
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{song_to_delete}'?"):
            os.remove(file_path)  # Delete from folder
            songs.pop(selected_index[0])  # Remove from list
            listbox_item.delete(selected_index[0])  # Remove from Listbox

            # Update current song if needed
            if songs:
                listbox_item.select_set(0)
                current_song = songs[0]
            else:
                current_song = ""

            messagebox.showinfo("Success", f"Deleted '{song_to_delete}' successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Could not delete file: {e}")

def clearList():
    songs.clear()
    listbox_item.delete(0, END) 

listbox_frame = Frame(frame1, bg='lightgray')
listbox_frame.grid(row=0, column=0, sticky='nsew')

listbox_item = Listbox(listbox_frame, listvariable=None, selectmode=SINGLE)
listbox_item.pack(expand=True, fill=BOTH)

listbox_control_button_frame = Frame(frame1, bg='darkgray')
listbox_control_button_frame.grid(row=0, column=1, sticky='nsew')

delete_song_btn = Button(listbox_control_button_frame,text='🗑️Delete Song',borderwidth=0,width=15, command=delete_selected_song)
delete_song_btn.pack(pady=20)

load_folder_btn = Button(listbox_control_button_frame,text='load Songs',borderwidth=0,width=15,command=load_music)
load_folder_btn.pack(pady=20)

clear_list_btn = Button(listbox_control_button_frame,text='❌Clear List',borderwidth=0,width=15, command=clearList)
clear_list_btn.pack(pady=20)

frame1.grid_columnconfigure(0, weight=4)
frame1.grid_columnconfigure(1, weight=1)
frame1.grid_rowconfigure(0, weight=1)

startup()

# ✅ frame 2 in tab one
frame2 = Frame(
    tab1,
    width=500,
    height=500,
    bg='red'
)
frame2.grid(row=0, column=1, padx=20, pady=5,sticky="ns")
frame2.grid_propagate(False)

frame2.grid_columnconfigure(0, weight=1)
frame2.grid_rowconfigure(2, weight=1)

video_data = {}
# ✅Function to search for a song and update the Listbox
def search_songs():
    query = search_var.get()
    result_listbox.delete(0, END)
    video_data.clear()

    results = search_for_song(query)
    if isinstance(results,list):
        for index, (video_title, video_url, video_id) in enumerate(results, 1):
            result_listbox.insert(END, f"{index}. {video_title}")
            video_data[index] = video_url
    else:
        result_listbox.insert(END, results)


# ✅search function
def search_for_song(SEARCH_QUERY):
    BASE_URL = "https://www.googleapis.com/youtube/v3/search"
    
    params = {
        "part": "snippet",
        "q": SEARCH_QUERY,
        "type": "video",
        "key": API_KEY,
        "maxResults": 5
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
    
        if "items" in data and data["items"]:
            results = []
            for index, item in enumerate(data['items'],1):            
                video_title = item['snippet']['title']
                video_id = item["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                results.append([video_title,video_url,video_id])
            return results
        else:
            return 'No song found'
    except requests.exceptions.ConnectionError:
        return 'Error: No internet connection.'
    except requests.exceptions.HTTPError as err:
        return f'HTTP Error: {err.response.status_code}'
    except requests.exceptions.RequestException:
        return 'Error: Something went wrong while fetching data.'


download_thread = None
stop_download = False
progress_window = None
progress_label = None
save_path = ""

# ✅ Function to get the selected video URL
def get_video_url(index):
    return video_data.get(index + 1)

# ✅ Function to download audio
def download_audio(video_url, save_path):
    global stop_download
    stop_download = False  # Reset the cancellation flag

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': save_path,  # Save to selected path
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    try:
        update_progress("⬇ Downloading...") 

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

            if not stop_download:
                close_progress_window()
                messagebox.showinfo('Download complete','Video Downloaded')
                
            else:
                messagebox.showinfo('Download cancelled', 'Download Cancelled')

    except Exception as e:
        update_progress(f"❌ Error: {str(e)}", "red")

    close_progress_window()

# ✅ Function to start the download process
def start_download():
    global download_thread, progress_window, progress_label, save_path

    selected = result_listbox.curselection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a song to download!")
        return

    index = selected[0]
    text = result_listbox.get(index)

    if ". " in text:
        title = text.split(". ", 1)[1]
    else:
        title = "Downloaded_Audio"

    video_url = get_video_url(index)  # Get video URL

    if not video_url:
        messagebox.showerror("Error", "Video URL not found!")
        return

    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()

    save_path = asksaveasfilename(
        title="Save As",
        initialfile=safe_title
    )

    if not save_path:
        return

    # Create progress window
    progress_window = Toplevel()
    progress_window.title("Download Progress")
    progress_window.geometry("300x100")
    progress_window.resizable(False, False)

    progress_label = Label(progress_window, text="Starting download...", font=("Helvetica", 12))
    progress_label.pack(pady=10)

    cancel_btn = Button(progress_window, text="Cancel", font=("Helvetica", 12), bg="red", fg="white", command=cancel_download)
    cancel_btn.pack(pady=5)

    # Run download in a thread
    download_thread = threading.Thread(target=download_audio, args=(video_url, save_path))
    download_thread.start()

# ✅ Function to track and update progress
def progress_hook(d):
    if stop_download:
        raise yt_dlp.utils.DownloadCancelled('Download cancelled')

    if d['status'] == 'downloading':
        update_progress(f"⬇ Downloading...")

# ✅ Function to update progress text dynamically
def update_progress(message, color="black"):
    if progress_label:
        progress_label.config(text=message, fg=color)
        progress_label.update_idletasks()  # Ensure UI updates immediately

# ✅ Function to cancel download
def cancel_download():
    global stop_download
    stop_download = True
    update_progress("⚠ Cancelling...", "red")

# ✅ Function to close progress window
def close_progress_window():
    if progress_window:
        progress_window.destroy()

# ✅ Title label
youtube_label = Label(frame2, text="Get song from YouTube", font=("Helvetica", 14, "bold"))
youtube_label.grid(row=0, column=0, pady=10, padx=10, sticky="n")

# ✅ Input box for search
search_var = StringVar()
search_entry = Entry(frame2, textvariable=search_var, font=("Helvetica", 12), width=30)
search_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

# ✅ Search button
search_button = Button(frame2, text="Search", font=("Helvetica", 12), bg="lightblue", command=search_songs)
search_button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# ✅ Listbox for displaying results
listbox_frame = Frame(frame2)
listbox_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

result_listbox = Listbox(listbox_frame, font=("Helvetica", 9), height=8, selectmode=SINGLE)
result_listbox.pack(expand=True, fill=BOTH)

# ✅ Buttons below listbox
button_frame = Frame(frame2)
button_frame.grid(row=3, column=0, columnspan=2, pady=10)

download_button = Button(button_frame, text="Download", font=("Helvetica", 12), bg="green", fg="white" ,command=start_download)
download_button.pack(side=LEFT, padx=5, ipadx=10)

# ✅frame 3 in tab one
frame3= Frame(
    tab1,
    height=200,
)
frame3.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

frame3.grid_columnconfigure(0, weight=1)
frame3.grid_columnconfigure(1, weight=1)
frame3.grid_columnconfigure(2, weight=1)

# ✅music control functions and buttons
shuffle_mode = False
def toggle_shuffle():
    """Toggle shuffle mode on/off."""
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    shuffle_btn.config(image=shuffle_on_btn_image if shuffle_mode else shuffle_off_btn_image)

def play_music():
    global current_song, paused
    selected_index = listbox_item.curselection()[0]
    current_song = songs[selected_index]
    title_text.config(text=f"{current_song}")
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.load(os.path.join(tab1.directory, current_song))
        pygame.mixer.music.play()
        update_time() 
        check_song_end()

def check_song_end():
    if not pygame.mixer.music.get_busy() and not paused:
        next_music()
    else:
        tab1.after(1000, check_song_end)

def pause_music():
    global paused
    pygame.mixer.music.pause()
    paused = True

def next_music():
    global current_song, paused
    try:
        current_index = listbox_item.curselection()[0]

        if shuffle_mode:
            new_index = random.randint(0, len(songs) - 1)
        else:
            new_index = current_index + 1

        if new_index >= len(songs):
            new_index = 0  

        listbox_item.selection_clear(0, END)
        listbox_item.select_set(new_index)
        listbox_item.activate(new_index)
        current_song = songs[new_index]

        if not paused:
            play_music()

    except IndexError:
        pass


def previous_music():
    global current_song, paused
    try:
        current_index = listbox_item.curselection()[0]

        if shuffle_mode:
            new_index = random.randint(0, len(songs) - 1)
        else:
            new_index = current_index - 1        

        if new_index >= 0:
            listbox_item.selection_clear(0, END)
            listbox_item.select_set(new_index)
            listbox_item.activate(new_index)
            current_song = songs[new_index]
            play_music()
    except IndexError:
        pass

def update_time():
    if pygame.mixer.music.get_busy():
        elapsed_time = pygame.mixer.music.get_pos() // 1000  
        total_time = MP3(os.path.join(tab1.directory, current_song)).info.length 

        elapsed_formatted = time.strftime('%M:%S', time.gmtime(elapsed_time))
        total_formatted = time.strftime('%M:%S', time.gmtime(total_time))

        duration_label.config(text=f"{elapsed_formatted} / {total_formatted}")
        tab1.after(1000, update_time)

def set_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)

# ✅Store volume level before muting
prev_volume = 0.5
muted = False

def toggle_mute():
    global muted, prev_volume

    if muted:
        pygame.mixer.music.set_volume(prev_volume)
        volume_slider.set(prev_volume * 100)
        mute_control_btn.config(image=mute_btn_image)
    else:
        prev_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0)
        volume_slider.set(0)
        mute_control_btn.config(image=unmute_btn_image)

    muted = not muted 

# ✅ Title and duration
title_frame = Frame(frame3)
title_frame.grid(row=0, column=0, columnspan=3, pady=0, sticky="ew")

title_label = Label(title_frame, text="Now playing:", font=("Helvetica", 14))
title_label.pack(side=LEFT, padx=10)

title_text = Label(title_frame, text="music.mp3", font=("Helvetica", 14), width=70)
title_text.pack(side=LEFT, padx=10)

duration_label = Label(title_frame, text="00:00 / 00:00", font=("Helvetica", 14))
duration_label.pack(side=LEFT, padx=10)

# ✅ Buttons Section
button_frame = Frame(frame3)
button_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

# ✅components inside frame3

# ✅icon images 32x32 
play_btn_img = PhotoImage(file='images/play-button.png')
pause_btn_img = PhotoImage(file='images/pause.png')
next_btn_img = PhotoImage(file='images/next.png')
previous_btn_img = PhotoImage(file='images/previous.png')
shuffle_on_btn_image = PhotoImage(file='images/shuffle.png')
shuffle_off_btn_image = PhotoImage(file='images/shuffle-arrows.png')
mute_btn_image = PhotoImage(file='images/mute.png')
unmute_btn_image = PhotoImage(file='images/volume.png')

for i in range(6):
    button_frame.grid_columnconfigure(i, weight=1)

previous_btn = Button(button_frame, image=previous_btn_img, borderwidth=0,command=previous_music)
play_btn = Button(button_frame, image=play_btn_img, borderwidth=0,command=play_music)
pause_btn = Button(button_frame, image=pause_btn_img, borderwidth=0,command=pause_music)
next_btn = Button(button_frame, image=next_btn_img, borderwidth=0, command=next_music)
shuffle_btn = Button(button_frame, image=shuffle_off_btn_image, borderwidth=0, command=toggle_shuffle)
mute_control_btn = Button(button_frame, image=mute_btn_image, borderwidth=0, command=toggle_mute)

previous_btn.grid(row=0, column=0, padx=5, sticky="ew")
play_btn.grid(row=0, column=1, padx=5, sticky="ew")
pause_btn.grid(row=0, column=2, padx=5, sticky="ew")
next_btn.grid(row=0, column=3, padx=5, sticky="ew")
shuffle_btn.grid(row=0, column=4, padx=5, sticky="ew")
mute_control_btn.grid(row=0, column=5, padx=5, sticky="ew")

# ✅ Volume Slider
volume_slider = Scale(button_frame, from_=0, to=100, orient=HORIZONTAL, length=300, label="Volume", command=set_volume)
volume_slider.set(50)
volume_slider.grid(row=0, column=6, columnspan=3)

# tab 2 in the notebook
def get_channel_id():
    if not youtube:
        print("YouTube API is not authenticated.")
        return None
    try:
        request = youtube.channels().list(
            part="snippet,contentDetails",
            maxResults=25,
            mine=True
        )
        response = request.execute()
        if not response.get("items"):
            print("No channels found for this user.")
            return None
        
        return response['items'][0]['id']
    except HttpError as e:
        print(f"API Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching channel ID: {e}")
        
channel_id = get_channel_id()

def get_playlist_id(channelid):
    if not channelid:
       return []
    try:
        request = youtube.playlists().list(
            part="snippet",
            channelId=channelid
        )
        response = request.execute()
        if not response.get("items"):
            print("No playlists found for this channel.")
            return []
        
        return [
            {"id": item["id"], "title": item["snippet"]["title"]}
            for item in response.get("items")
        ]
    except HttpError as e:
        print(f"API Error: {e}")
        return []
    except Exception as e:
        print(f"❌ Error fetching Playlist ID: {e}")

playlist_ids = get_playlist_id(channel_id)

def extract_artist_and_title(songs):
    """Extracts artist and song title from video title while removing brackets and their content."""
    extracted_data =[]

    for song in songs:
        music_info = song[0]

        parts = music_info.split(':', 1)
        title_part = parts[0]
        url = parts[1].strip() if len(parts) > 1 else None

        # Remove text inside brackets
        clean_title = re.sub(r'\s*[\(\[].*?[\)\]]', '', title_part.strip())

        # Split into artist and title
        if '-' in clean_title:
            artist, song_title = clean_title.split('-', 1)
            artist = artist.strip()
            song_title = song_title.strip()
        else:
            artist, song_title = "Unknown", clean_title.strip()

        extracted_data.append([ artist, song_title, url])
    return extracted_data

def get_songs_from_playlist( playlist_ids):
    playlist_id = [item['id'] for item in playlist_ids if item['title'] == 'pieces']
    if not playlist_id:
        return []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId= playlist_id[0],
        maxResults = 25
    )
    response = request.execute()
    songs = []
    for item in response.get('items', []):
        video_title = item['snippet']['title']
        video_id = item['snippet']['resourceId']['videoId']
        video_details = f'{video_title} : https://www.youtube.com/watch?v={video_id}'
        songs.append([video_details])
    clean_songs = extract_artist_and_title(songs)
    return clean_songs


def load_yt_songs():
    """Fetches songs from YouTube playlist and populates the listbox."""
    songs_listbox2.delete(0, 'end')
    playlist_id = playlist_ids
    songs = get_songs_from_playlist(playlist_id)

    for artist, title, url in songs:
        songs_listbox2.insert('end', f"{artist} - {title}")


def get_playlist_ID():
    playlists = []
    offset=0
    limit=50
    while True:
        response = sp.current_user_playlists(limit=limit,offset=offset)

        if not response['items']:
            break

        playlists.extend(response['items'])
        offset+=limit
    if not playlists:
        print('No Playlists found.')
        return {}
    
    playlists_items = {playlist['name']: playlist['id'] for playlist in playlists}
    
    return {"yt-music-playlist": playlists_items["yt-music-playlist"]} if "yt-music-playlist" in playlists_items else {}
sp_playlistID = get_playlist_ID()

def get_playlist_songs(sp_playlistID):
    all_songs = {}
    
    for playlist_name, playlist_id in sp_playlistID.items():
        tracks = []
        offset = 0
        limit = 100

        while True:
            response = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)
            tracks.extend(response['items'])

            if len(response['items']) < limit:
                break

            offset += limit

        if not tracks:
            print(f"No songs found in playlist: {playlist_name}")
            continue

        songs = {
            track['track']['name']:[ ', '.join(
                artist['name'] for artist in track['track']['artists']
            ),track['track']['uri']] for track in tracks if track.get('track')
        }

        all_songs[playlist_name] = songs
    return all_songs

def find_song_by_uri(song_uri, data, playlist_name):
    if playlist_name not in data:
        return f"Playlist '{playlist_name}' not found."

    for song_title, details in data[playlist_name].items():
        artist, uri = details
        if uri == song_uri:
            return True, f"Song: {song_title}, Artist: {artist}"

    return False,f"Song not found in '{playlist_name}'."

def add_song_to_playlist(track_uri,playlist_name='yt-music-playlist'):
    playlist_id = sp_playlistID.get(playlist_name)

    if not playlist_id:
        print(f"{playlist_name} not found.")
        return
    data = get_playlist_songs(sp_playlistID)    
    found,message = find_song_by_uri(track_uri, data,playlist_name)
    if found:
        print(f"Cannot add Song because is already in playlist: {playlist_name}: {message}")
        return
    try:
        sp.playlist_add_items(playlist_id, [track_uri])
        print(f"Song added to playlist {playlist_name}!")
    except Exception as e:
        print(f"Error adding song: {e}")

def search_song(song_name=None, artist_name=None):
    """Searches for a song on Spotify and returns its details."""
    if not song_name and not artist_name:
        print("⚠️ Error: No search query provided.")
        return "⚠️ Please enter a song title or artist name."

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=YOUR_APP_CLIENT_ID,
            client_secret=YOUR_APP_CLIENT_SECRET,
            redirect_uri=YOUR_APP_REDIRECT_URI,
            scope="playlist-read-private"
        )
    )

    # Build a valid search query
    if song_name and artist_name:
        query = f"track:{song_name} artist:{artist_name}"
    elif artist_name:
        query = f"artist:{artist_name}"
    else:
        query = f"track:{song_name}"

    result_limit = 10 if artist_name and not song_name else 1

    try:
        results = sp.search(q=query, limit=result_limit, type='track')
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return "⚠️ Unable to fetch results. Check API access."

    music_details = []

    for track in results['tracks']['items']:
        artist = ', '.join(artist['name'] for artist in track['artists'])
        title = track['name']
        album = track['album']['name']
        uri = track['uri']

        music_details.append({'Artist': artist, 'Title': title, 'Album': album, 'URI': uri})

    return music_details if music_details else "⚠️ No song found."

def remove_song_from_playlist(track_uri, playlist_name="yt-music-playlist"):
    """Removes a song from the specified playlist."""
    
    playlist_id = sp_playlistID.get(playlist_name)

    if not playlist_id:
        print(f"Playlist '{playlist_name}' not found.")
        return

    try:
        sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])
        return f"Song removed from playlist {playlist_name}!"
    except Exception as e:
        return f"Error removing song: {e}"

def load_spotify_songs():
    """Fetches songs from Spotify and populates songs_listbox1."""
    songs_listbox1.delete(0, 'end')  # Clear existing items

    # Fetch songs from Spotify playlist
    spotify_songs = get_playlist_songs(sp_playlistID)

    # Extract songs from 'yt-music-playlist' if it exists
    if "yt-music-playlist" in spotify_songs:
        for title, (artist, uri) in spotify_songs["yt-music-playlist"].items():
            songs_listbox1.insert('end', f"{artist} - {title}")

def search_and_display():
    """Fetches search results based on user input and displays them in the listbox."""
    # Get the user input from entry fields
    artist = artist_entry_var.get().strip()
    title = title_entry_var.get().strip()

    # Clear previous search results
    search_results.delete(0, END)

    if not artist and not title:
        search_results.insert(END, "⚠️ Please enter a song title or artist name.")
        return

    # Fetch search results
    results = search_song(song_name=title, artist_name=artist)

    if isinstance(results, str):  # If no song was found, results will be a string message
        search_results.insert(END, results)
    else:
        for song in results:
            display_text = f"{song['Title']} - {song['Artist']} ({song['Album']})"
            search_results.insert(END, display_text)

def add_selected_song_to_playlist():
    """Adds the selected song from the search results to a Spotify playlist."""
    try:
        selected_index = search_results.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a song first.")
            return

        selected_song = search_results.get(selected_index[0])

        # Fetch latest search results using user inputs
        artist = artist_entry_var.get().strip()
        title = title_entry_var.get().strip()
        search_results_data = search_song(song_name=title, artist_name=artist)

        if isinstance(search_results_data, str):  # No results found
            messagebox.showerror("Error", search_results_data)
            return

        # Find the matching song in search results
        for song in search_results_data:
            display_text = f"{song['Title']} - {song['Artist']} ({song['Album']})"
            if display_text == selected_song:
                track_uri = song['URI']
                break
        else:
            messagebox.showerror("Error", "Could not retrieve song details.")
            return

        # Add song to playlist
        add_song_to_playlist(track_uri)

        # Show success message
        messagebox.showinfo("Success", "Song added to playlist!")

        # Reload the Spotify playlist
        load_spotify_songs()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add song: {e}")

def remove_selected_song():
    """Removes the selected song from the playlist after confirmation."""
    try:
        # Get selected song from the listbox
        selected_index = songs_listbox1.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a song first.")
            return
        
        selected_song = songs_listbox1.get(selected_index[0])  # Get song text
        artist, title = selected_song.split(" - ", 1)  # Extract artist & title
        
        # Retrieve song URI from playlist data
        playlist_data = get_playlist_songs(sp_playlistID)
        yt_music_playlist = playlist_data.get("yt-music-playlist", {})

        track_uri = None
        for song_title, (song_artist, uri) in yt_music_playlist.items():
            if song_title == title and song_artist == artist:
                track_uri = uri
                break

        if not track_uri:
            messagebox.showerror("Error", "Could not find the song's URI.")
            return

        # Ask user for confirmation
        confirm = messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{title}' from the playlist?")
        if not confirm:
            return  # User canceled

        # Remove song from playlist
        remove_song_from_playlist(track_uri)

        # Show success message
        messagebox.showinfo("Success", f"'{title}' has been removed from the playlist!")

        # Refresh the listbox
        load_spotify_songs()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove song: {e}")

def add_selected_songs_to_spotify():
    """Adds selected YouTube songs to the Spotify playlist."""
    try:
        # Get selected songs from the listbox
        selected_indices = songs_listbox2.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select at least one song.")
            return
        
        added_songs = []
        skipped_songs = []

        for index in selected_indices:
            selected_song = songs_listbox2.get(index)  # Get song text
            artist, title = selected_song.split(" - ", 1)  # Extract artist & title
            
            # Search for the song on Spotify
            results = search_song(song_name=title, artist_name=artist)
            if not results:
                skipped_songs.append(f"{artist} - {title} (Not Found)")
                continue  # Skip to the next song

            # Get the first matching Spotify track URI
            track_uri = results[0]['URI']

            # Check if the song is already in the playlist
            data = get_playlist_songs(sp_playlistID)
            found, _ = find_song_by_uri(track_uri, data, "yt-music-playlist")

            if found:
                skipped_songs.append(f"{artist} - {title} (Already in Playlist)")
                continue  # Skip to the next song

            # Add song to playlist
            add_song_to_playlist(track_uri)
            added_songs.append(f"{artist} - {title}")

        # Show a final message summarizing what happened
        message = ""
        if skipped_songs:
            message += "⚠️ **Skipped Songs:**\n" + "\n".join(skipped_songs)
        if added_songs:
            message += " Songs Added"
        messagebox.showinfo("Process Completed", message.strip())

        # Refresh the Spotify listbox
        load_spotify_songs()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add songs: {e}")
# Tab 2
tab2 = Frame(main_tab, bg='white')

tab2.grid_rowconfigure(1, weight=1)
tab2.grid_columnconfigure(0, weight=1)
tab2.grid_columnconfigure(1, weight=1)

# --- Search Section ---
search_frame = LabelFrame(tab2, text="Search", padx=10, pady=5)
search_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
tab2.grid_rowconfigure(0, weight=0)

search_frame.grid_columnconfigure(0, weight=1)
search_frame.grid_columnconfigure(1, weight=2)
search_frame.grid_columnconfigure(2, weight=0)

# Artist Input
Label(search_frame, text="Artist:").grid(row=0, column=0, pady=5, sticky="w")

artist_entry_var = StringVar()
artist_entry = Entry(search_frame, textvariable=artist_entry_var)
artist_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Title Input
Label(search_frame, text="Title:").grid(row=1, column=0, pady=5, sticky="w")

title_entry_var = StringVar()
title_entry = Entry(search_frame, textvariable=title_entry_var)
title_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Search Button on the side
search_btn = Button(search_frame, text="Search", command=search_and_display)
search_btn.grid(row=2, column=0, rowspan=2, padx=5, pady=5, sticky="ns")

# Create a horizontal scrollbar
search_scroll_x = Scrollbar(search_frame, orient=HORIZONTAL)
search_scroll_x.grid(row=2, column=2, sticky="ew", padx=5)

# Create a vertical scrollbar
search_scroll_y = Scrollbar(search_frame, orient=VERTICAL)
search_scroll_y.grid(row=0, column=3, rowspan=2, sticky="ns")

# Search Results Listbox with scrollbars
search_results = Listbox(
    search_frame, height=7, width=100, 
    xscrollcommand=search_scroll_x.set, 
    yscrollcommand=search_scroll_y.set
)
search_results.grid(row=0, column=2, rowspan=2, padx=5, sticky="nsew")

# Link scrollbars to listbox
search_scroll_x.config(command=search_results.xview)
search_scroll_y.config(command=search_results.yview)

# Buttons Frame
buttons_frame = Frame(search_frame)
buttons_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=5, sticky="ns")

add_to_spotify_btn = Button(buttons_frame, text="Add to Spotify", command=add_selected_song_to_playlist)
add_to_spotify_btn.pack(pady=5, fill=X)

# --- Left Listbox ---
left_songs_frame = LabelFrame(tab2, text="Spotify Playlist Songs", padx=10, pady=10)
left_songs_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# Frame for Listbox and Scrollbars
left_listbox_frame = Frame(left_songs_frame)
left_listbox_frame.pack(fill=BOTH, expand=True)

# Scrollbars for left listbox
left_scroll_y = Scrollbar(left_listbox_frame, orient=VERTICAL)
left_scroll_x = Scrollbar(left_listbox_frame, orient=HORIZONTAL)

# Left Listbox
songs_listbox1 = Listbox(
    left_listbox_frame, width=50, yscrollcommand=left_scroll_y.set, xscrollcommand=left_scroll_x.set
)
songs_listbox1.pack(fill=BOTH, expand=True, padx=5, pady=5)

# Configure scrollbars
left_scroll_y.config(command=songs_listbox1.yview)
left_scroll_x.config(command=songs_listbox1.xview)

# Place scrollbars
left_scroll_y.pack(side=RIGHT, fill=Y)
left_scroll_x.pack(side=BOTTOM, fill=X)

# Buttons under left listbox (OUTSIDE the scrollbars)
buttons_left_frame = Frame(left_songs_frame)
buttons_left_frame.pack(pady=5, fill=X)

button1_left = Button(buttons_left_frame, text="Load Songs", command=load_spotify_songs)
button1_left.pack(side=LEFT, padx=5, pady=5, expand=True)

button2_left = Button(buttons_left_frame, text="Remove from Playlist", command=remove_selected_song)
button2_left.pack(side=LEFT, padx=5, pady=5, expand=True)

# --- Right Listbox ---
right_songs_frame = LabelFrame(tab2, text="YT-Playlist-Songs", padx=10, pady=10)
right_songs_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

# Frame for Listbox and Scrollbars
right_listbox_frame = Frame(right_songs_frame)
right_listbox_frame.pack(fill=BOTH, expand=True)

# Scrollbars for right listbox
right_scroll_y = Scrollbar(right_listbox_frame, orient=VERTICAL)
right_scroll_x = Scrollbar(right_listbox_frame, orient=HORIZONTAL)

# Right Listbox
songs_listbox2 = Listbox(
    right_listbox_frame, width=50, yscrollcommand=right_scroll_y.set, xscrollcommand=right_scroll_x.set,selectmode=MULTIPLE
)
songs_listbox2.pack(fill=BOTH, expand=True, padx=5, pady=5)

# Configure scrollbars
right_scroll_y.config(command=songs_listbox2.yview)
right_scroll_x.config(command=songs_listbox2.xview)

# Place scrollbars
right_scroll_y.pack(side=RIGHT, fill=Y)
right_scroll_x.pack(side=BOTTOM, fill=X)

# Buttons under right listbox (OUTSIDE the scrollbars)
buttons_right_frame = Frame(right_songs_frame)
buttons_right_frame.pack(pady=5, fill=X)

button1_right = Button(buttons_right_frame, text="Load Songs", command=load_yt_songs)
button1_right.pack(side=LEFT, padx=5, pady=5, expand=True)

button2_right = Button(buttons_right_frame, text="Add to Spotify Playlist",command=add_selected_songs_to_spotify)
button2_right.pack(side=LEFT, padx=5, pady=5, expand=True)

main_tab.add(
    tab1,
    text='Music Player'
)
main_tab.add(
    tab2,
    text='Playlists'
)

window.mainloop()