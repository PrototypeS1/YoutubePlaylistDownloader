import os
import re
import streamlit as st
import yt_dlp
from main import adjust_directory_based_on_playlist

# Initialize Streamlit session state for log messages if not already done
if 'log_messages' not in st.session_state:
    st.session_state['log_messages'] = []

# Define the log function
def log(message):
    """Appends a message to the log and updates the log display."""
    if message:
        st.session_state['log_messages'].append(message)
        # Update the text area with the log messages
        log_area.text_area("Download Log", "\n".join(st.session_state['log_messages']),
                           height=300, disabled=True, key="log_area")

# Define the layout
st.title("YouTube Playlist Downloader")

# Input fields for URL and download settings
playlist_url = st.text_input("Enter Playlist URL:")
destination_folder = st.text_input("Enter Destination Folder:", value=os.path.join(os.path.expanduser('~'), 'Desktop'))
ffmpeg_folder = st.text_input("Enter FFmpeg Folder (optional):")
format_choice = st.selectbox("Choose Format", ["mp3", "mp4"], index=0)

# Create a placeholder for the log text area
log_area = st.empty()

def download_worker():
    """Handles the download process and logs messages."""
    log("Starting download...")
    
    # Set up yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best' if format_choice == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(playlist_title)s', '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio' if format_choice == 'mp3' else None,
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if format_choice == 'mp3' else None,
    }

    # Download the playlist
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        log("Download completed successfully.")
    except Exception as e:
        log(f"Download failed: {e}")

def progress_hook(d):
    """Handles progress updates from yt-dlp."""
    if d['status'] == 'downloading':
        percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        log(f"Downloading: {percent:.2f}%")
    elif d['status'] == 'finished':
        adjust_directory_based_on_playlist(d, destination_folder)
        log(f"Done downloading video: {d['filename']}")

# Start download when the button is pressed
if st.button("Start Download"):
    download_worker()

# No clear logs button is needed
