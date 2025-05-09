# YouTube Playlist Transcript Downloader

Alright, so here's the deal. I was staring at this massive YouTube playlist, right? And I needed all those transcripts to feed into Notebook LM. Clicking through each video, finding the transcript, copying, pasting... ain't nobody got time for that! 😩

So, like any lazy programmer faced with a tedious task i wrote this script. It's a nifty little Streamlit app that grabs all the transcripts from a YouTube playlist and bundles them up into a nice, neat ZIP file for you.

## How to Clone this project

Setting this up is pretty chill. Here’s what you gotta do:

1.  **Clone or Download:**
    First things first, get the code onto your machine. If you know git, clone it. If not, just download the files.

2.  **Install the Dependencies:**
    Open up your terminal or command prompt and type this in:
    ```bash
    pip install streamlit youtube-dl youtube-transcript-api
    ```

3.  **Run the App:**
    Navigate to the folder where you saved the `app.py` file in your terminal and run:
    ```bash
    streamlit run app.py
    ```
    Your web browser should pop open with the app.


Now go and dump those transcripts into Notebook LM or wherever you want.
