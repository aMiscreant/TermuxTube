# TermuxTube

**TermuxTube** is an open-source project designed to automate the creation, editing, and uploading of YouTube videos and Shorts directly from your Android device using Termux. It offers features like scene detection, video splitting, AI-generated titles, and seamless YouTube uploads.

With **TermuxTube**, you can efficiently create engaging YouTube Shorts and regular videos entirely from your mobile device — no computer required!

---

## 📦 Features

- **Mobile-Friendly**: Fully works within Termux on Android devices.
- **AI-Powered Title Generation**: Automatically generates and sanitizes video titles from audio content.
- **Scene Detection**: Automatically detects scenes in videos and splits them into smaller, manageable segments.
- **Clip Creation**: Converts video segments into clips for YouTube Shorts.
- **YouTube Upload Automation**: Uploads both standard YouTube videos and Shorts with descriptions, tags, and privacy settings.
- **Open-Source & Free**: All features are free and open-source under the GPL license.

---

## 🚀 Getting Started

### Prerequisites

1. **Install Termux**:  
   Get Termux from [Google Play Store](https://play.google.com/store/apps/details?id=com.termux) or [F-Droid](https://f-droid.org/packages/com.termux/).

2. **Install Python**:  
   Make sure Python 3.x is installed:

   ```bash
   pkg install python

Google API Setup:
Create a new project in the Google Cloud Console, enable the YouTube Data API v3, and download the OAuth 2.0 credentials (client_secret.json).

Install Required Dependencies:
Use pip to install the necessary libraries.

    pip install -r requirements.txt

🧑‍💻 How It Works
1. Video Splitting

    splitter.py: Splits longer videos (greater than 15 minutes) into smaller segments, making them suitable for YouTube Shorts.

    python splitter.py /path/to/video.mp4

2. Clip Creation

    long_to_clips.py: Converts the split video segments into clips for YouTube Shorts.

    python long_to_clips.py /path/to/split/video/folder

3. Title Generation

    generate_titles.py: Uses AI to generate titles based on the audio from the video clips. It also cleans up titles by removing any profanity.

    python generate_titles.py /path/to/video/folder/

4. YouTube Uploading

    youtube_uploader.py: Uploads the generated clips to YouTube, automatically handling video titles, descriptions, tags, and privacy settings.

    python youtube_uploader.py /path/to/video/folder/

🛠️ Customizations

    Custom Tags: Tags are auto-generated based on folder names. For example, a folder named "JRE" will get tags like ["Joe Rogan", "Podcast", "JRE Clips"].

    Clip Length: Modify the segment length in long_to_clips.py if you want shorter or longer clips for YouTube Shorts.

    OAuth Setup: The script handles OAuth 2.0 authorization using your client_secret.json file.

🎯 Full Workflow

    Split the video using splitter.py.

    Create the Shorts clips using long_to_clips.py.

    Generate titles using generate_titles.py.

    Upload to YouTube with youtube_uploader.py.

🤝 Contributing

Feel free to fork this repo and contribute! If you find bugs or have suggestions, open an issue, and I'll review it as soon as possible.
📜 License

This project is open-source and available under the GPL-3.0 License. See the LICENSE file for more details.
🏁 Enjoy creating and uploading YouTube Shorts with ease on your mobile device using TermuxTube!