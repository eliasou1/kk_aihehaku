from flask import Flask, render_template, request
from googleapiclient.discovery import build
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        channel_id = 'UCBHvy-pjrxS88ZqiJXS6Ydw'
        results = search_videos(keyword, channel_id)
        return render_template('results.html', keyword=keyword, results=results)
    else:
        return render_template('search.html')

def search_videos(keyword, channel_id):
    youtube = build('youtube', 'v3', developerKey='AIzaSyD5EEJLDVKMQJP6dgApelAqezrtmvaXGjg')

    # Call the search.list method to search for videos
    search_response = youtube.search().list(
        q=keyword,
        type='video',
        channelId=channel_id,
        part='id,snippet',
        maxResults=10
    ).execute()

    # Get the video IDs from the search results
    video_ids = []
    for search_result in search_response.get('items', []):
        video_ids.append(search_result['id']['videoId'])

    # Call the videos.list method to retrieve the video descriptions
    video_response = youtube.videos().list(
        id=','.join(video_ids),
        part='snippet'
    ).execute()

    # Create a dictionary to store the video information
    videos = {}
    for video_result in video_response.get('items', []):
        video_id = video_result['id']
        video_info = {
            'title': video_result['snippet']['title'],
            'description': video_result['snippet']['description'],
            'thumbnail': video_result['snippet']['thumbnails']['default']['url']
        }
        videos[video_id] = video_info

    # Filter the videos by the keyword
    filtered_videos = {}
    for video_id, video_info in videos.items():
        # Use regex to match the keyword even if it's part of another word
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        if pattern.search(video_info['description']):
            video_info['description'] = pattern.sub(keyword, video_info['description'])
            filtered_videos[video_id] = video_info

    return filtered_videos

if __name__ == '__main__':
    app.run(debug=True)
