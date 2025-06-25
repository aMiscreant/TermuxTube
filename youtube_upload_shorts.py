#!/usr/bin/env python3
import os
import json
import sys
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
UPLOADED_TRACKER = "uploaded.json"


def get_authenticated_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=8080, open_browser=False)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def get_tags_from_folder(folder_name):
    folder = folder_name.lower()
    if "jre" in folder:
        return ["Joe Rogan", "Podcast", "JRE Clips"]
    if "shawnryan" in folder:
        return ["Shawn Ryan", "Vigilance Elite", "Podcast"]
    return ["Podcast", "Shorts"]


def upload_video(youtube, video_path, title, description, tags):
    if not title.strip():
        print(f"[!] Skipping upload: Empty title for {video_path}")
        return None

    # Ensure title includes #Shorts
    if "#shorts" not in title.lower():
        title = title.strip() + " #Shorts"

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media = MediaFileUpload(video_path, mimetype="video/*", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    response = request.execute()
    print(f"[✓] Uploaded: {title}\n    → https://youtu.be/{response['id']}")
    return response['id']


def load_uploaded_tracker():
    if os.path.exists(UPLOADED_TRACKER):
        with open(UPLOADED_TRACKER, "r") as f:
            return json.load(f)
    return {}


def save_uploaded_tracker(tracker):
    with open(UPLOADED_TRACKER, "w") as f:
        json.dump(tracker, f, indent=2)


def main(folder_path):
    youtube = get_authenticated_service()
    uploaded = load_uploaded_tracker()

    if os.path.exists(os.path.join(folder_path, "titles.json")):
        folder_paths = [folder_path]
    else:
        folder_paths = [
            os.path.join(folder_path, d)
            for d in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, d))
        ]

    for dir_path in folder_paths:
        dir_name = os.path.basename(dir_path)

        titles_path = os.path.join(dir_path, "titles.json")
        desc_path = os.path.join(dir_path, "description.txt")
        if not os.path.exists(titles_path) or not os.path.exists(desc_path):
            print(f"[!] Skipping {dir_name}: titles.json or description.txt not found.")
            continue

        with open(titles_path, "r") as f:
            titles = json.load(f)
        with open(desc_path, "r") as f:
            description = f.read().strip()

        # Ensure #Shorts is in description
        if "#shorts" not in description.lower():
            description += "\n\n#Shorts"

        tags = get_tags_from_folder(dir_name)

        for video_file, title in titles.items():
            video_path = os.path.join(dir_path, video_file)

            # Skip already uploaded
            if video_file in uploaded:
                print(f"[⏩] Already uploaded: {video_file}")
                continue

            if not os.path.exists(video_path):
                print(f"[!] Video not found: {video_path}")
                continue

            try:
                video_id = upload_video(youtube, video_path, title, description, tags)
                if video_id:
                    uploaded[video_file] = video_id
                    save_uploaded_tracker(uploaded)
                    print("[⏳] Waiting 5 minutes before next upload...")
                    time.sleep(300)  # 5 minutes
            except Exception as e:
                print(f"[❌] Upload failed for {video_file}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube_uploader.py /path/to/Shorts")
        sys.exit(1)
    main(sys.argv[1])
