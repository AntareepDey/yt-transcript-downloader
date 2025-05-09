import re
import streamlit as st
from youtube_dl import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
import time
import zipfile
import os
import base64

# Page configuration
st.set_page_config(
    page_title="YouTube Transcript Downloader",
    page_icon="📝",
    layout="wide"  # Use wide layout for better spacing
)

# Theme configuration - using YouTube colors
youtube_red = "#FF0000"
youtube_orange = "#FF9900"

# Custom CSS for center alignment and YouTube gradient progress bar
st.markdown(f"""
<style>
    /* Center alignment for all content */
    .block-container {{
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    /* Center all text content */
    h1, h2, h3, p, .stMarkdown, .stText {{
        text-align: center !important;
    }}
    
    /* Center the YouTube Logo */
    .logo-container {{
        display: flex;
        justify-content: center;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }}
    
    /* Style the YouTube Logo */
    .youtube-logo {{
        width: 120px;
        height: auto;
    }}
    
    /* Center the input field container */
    .stTextInput {{
        display: flex;
        justify-content: center;
    }}
    
    /* File list styling - centered */
    .file-list {{
        max-height: 200px;
        overflow-y: auto;
        margin: 1rem auto;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
    }}
    
    .file-item {{
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
        border-left: 4px solid {youtube_red};
        text-align: left;
    }}
    
    .progress-label {{
        display: flex;
        justify-content: space-between;
        margin: 0.5rem auto;
        max-width: 100%;
    }}
    
    /* Center all alert/info messages */
    .stAlert {{
        text-align: center;
    }}
    
    /* Center download button */
    .download-button {{
        text-align: center;
        margin: 1rem auto;
    }}
</style>
""", unsafe_allow_html=True)

def sanitize_filename(title):
    return re.sub(r'[<>:\"/\\|?*]', '_', title)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """
    Generate a download link for a binary file
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/zip;base64,{bin_str}" download="{os.path.basename(bin_file)}" style="text-decoration:none;color:white;background-image:linear-gradient(to right, {youtube_red}, {youtube_orange});padding:10px 24px;border-radius:8px;font-weight:500;display:inline-block;">📥 Download {file_label}</a>'
    return href

# Main content
# App Header with YouTube logo properly centered
st.markdown('<div class="logo-container"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/800px-YouTube_full-color_icon_%282017%29.svg.png" class="youtube-logo"></div>', unsafe_allow_html=True)

# Title and description
st.title("YouTube Playlist Transcript Downloader",)
st.markdown("Extract and download transcripts from any YouTube playlist")

# Create columns for layout - using more space in the center
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Input field for playlist URL
    playlist_url = st.text_input("", placeholder="Enter YouTube Playlist URL")
    
    # Process button
    process_button = st.button("Process Playlist", type="primary", use_container_width=True)
    
    # Container for download status
    status_container = st.empty()
    progress_bar = st.empty()
    file_list_container = st.empty()
    
    # Download process
    if process_button:
        if not playlist_url:
            status_container.error("Please enter a valid YouTube playlist URL.")
        else:
            try:
                # Create temp directory for transcripts
                if not os.path.exists('transcripts'):
                    os.makedirs('transcripts')
                
                # Create a zip file to store all transcripts
                zip_path = "youtube_transcripts.zip"
                
                # Extract video entries from the playlist
                status_container.info("Fetching playlist information...")
                ydl_opts = {'extract_flat': True}
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(playlist_url, download=False)
                    videos = info['entries']
                    playlist_title = info.get('title', 'YouTube Playlist')
                
                # Initialize progress tracking
                total_videos = len(videos)
                completed_videos = 0
                successful_downloads = 0
                failed_videos = []
                downloaded_files = []
                
                status_container.info(f"Found {total_videos} videos in playlist: {playlist_title}")
                progress = progress_bar.progress(0)
                
                # Insert custom CSS for progress bar AFTER it's created
                # This ensures our styles override Streamlit's defaults
                st.markdown(f"""
                <style>
                
                /* Target the specific classes that Streamlit assigns */
                div[data-testid="stProgressBar"] div div {{
                    background-image: linear-gradient(to right, {youtube_orange},{youtube_red} ) !important;
                    background-color: transparent !important;
                }}
                
                /* Extremely specific selector for the progress bar fill */
                .st-cu, .st-f1{{
                    background-image: linear-gradient(to right, {youtube_orange},{youtube_red} ) !important;
                    background-color: transparent;
                }}
                </style>
                """, unsafe_allow_html=True)
                
                # Process each video and save its transcript
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for video in videos:
                        video_id = video['id']
                        title = video['title']
                        sanitized_title = sanitize_filename(title)
                        filename = f"{sanitized_title}_{video_id}.txt"
                        filepath = os.path.join('transcripts', filename)
                        
                        try:
                            # Update status
                            status_container.info(f"Processing: {title}")
                            
                            # Get transcript
                            transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            transcript_text = ' '.join([item['text'] for item in transcript])
                            
                            # Save transcript to file
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(transcript_text)
                            
                            # Add to zip
                            zipf.write(filepath, filename)
                            successful_downloads += 1
                            downloaded_files.append(title)
                            
                        except Exception as e:
                            failed_videos.append((title, str(e)))
                        
                        # Update progress
                        completed_videos += 1
                        progress.progress(completed_videos / total_videos)
                        
                        # Display list of processed files
                        file_list_html = "<div class='file-list'>"
                        for file in downloaded_files[-5:]:  # Show last 5 files
                            file_list_html += f"<div class='file-item'>✓ {file}</div>"
                        file_list_html += "</div>"
                        
                        file_list_container.markdown(f"""
                        <div class="progress-label">
                            <span>Processed: {completed_videos}/{total_videos}</span>
                            <span>Success: {successful_downloads}</span>
                        </div>
                        {file_list_html}
                        """, unsafe_allow_html=True)
                        
                        time.sleep(0.5)  # Reduce delay to make it faster
                
                # Show download link for the zip file
                if successful_downloads > 0:
                    status_container.success(f"✅ Completed! Successfully downloaded {successful_downloads} of {total_videos} transcripts")
                    st.markdown(f"""
                    <div class="download-button">
                        {get_binary_file_downloader_html(zip_path, f"{playlist_title} Transcripts")}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show failed downloads if any
                    if failed_videos:
                        st.write("⚠️ Failed downloads:")
                        for title, error in failed_videos:
                            st.write(f"- {title}: {error}")
                else:
                    status_container.error("❌ Could not download any transcripts from this playlist.")
                    
            except Exception as e:
                status_container.error(f"❌ Error processing playlist: {str(e)}")