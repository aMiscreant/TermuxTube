import os
import logging
import cv2
import yt_dlp
import argparse
import random
from moviepy import VideoFileClip, vfx

# ANSI escape codes for colored output
class Color:
    INFO = "\033[92m"  # Green
    WARNING = "\033[93m"  # Yellow
    ERROR = "\033[91m"  # Red
    RESET = "\033[0m"  # Reset to default


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def download_video(url):
    """Download video using yt_dlp."""
    logging.info(f"{Color.INFO}Downloading video from URL: {url}{Color.RESET}")
    ydl_opts = {
        'format': 'bestvideo[ext=webm]+bestaudio/best[ext=webm]',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            video_file = f"{video_title}.webm"
            logging.info(f"{Color.INFO}Downloaded: {video_file}{Color.RESET}")
            return video_file
    except Exception as e:
        logging.error(f"{Color.ERROR}Error downloading video: {e}{Color.RESET}")
        return None


def debug_video_properties(video_file):
    """Log properties of the video."""
    try:
        with VideoFileClip(video_file) as clip:
            duration = clip.duration
            fps = clip.fps
            resolution = clip.size
            logging.info(
                f"{Color.INFO}Video Properties - Duration: {duration:.2f} seconds, Resolution: {resolution}, FPS: {fps}{Color.RESET}")
    except Exception as e:
        logging.error(f"{Color.ERROR}Error retrieving properties for {video_file}: {e}{Color.RESET}")


def split_video(video_file, max_duration=600):
    """Split the video into sections no longer than max_duration."""
    clips_created = []
    try:
        with VideoFileClip(video_file) as clip:
            total_duration = clip.duration
            logging.info(f"{Color.INFO}Total duration of video: {total_duration:.2f} seconds{Color.RESET}")

            # Create segments
            start_time = 0
            clip_count = 0
            video_title = os.path.splitext(os.path.basename(video_file))[0]

            while start_time < total_duration:
                end_time = min(start_time + max_duration, total_duration)

                # Check if the segment is valid
                if end_time - start_time <= 0:
                    logging.warning(
                        f"{Color.WARNING}Skipping invalid segment from {start_time} to {end_time}{Color.RESET}")
                    break

                # Generate a unique output file name
                output_file = f"{video_title}_part_{clip_count}.mp4"

                try:
                    clip.subclip(start_time, end_time).write_videofile(output_file, codec='libx264', audio_codec='aac')
                    logging.info(
                        f"{Color.INFO}Created segment: {output_file} from {start_time} to {end_time}{Color.RESET}")
                    clips_created.append(output_file)
                except Exception as e:
                    logging.error(f"{Color.ERROR}Error creating segment {output_file}: {e}{Color.RESET}")

                start_time += max_duration
                clip_count += 1

    except Exception as e:
        logging.error(f"{Color.ERROR}Error splitting video {video_file}: {e}{Color.RESET}")

    return clips_created


def detect_scenes(video_file):
    """Detect scenes in the video using OpenCV."""
    logging.info(f"{Color.INFO}Detecting scenes in: {video_file}{Color.RESET}")
    cap = cv2.VideoCapture(video_file)
    scenes = []
    ret, prev_frame = cap.read()

    if not ret:
        logging.warning(f"{Color.WARNING}Failed to read video: {video_file}")
        cap.release()
        return scenes

    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    frame_count = 0

    while True:
        ret, current_frame = cap.read()
        if not ret:
            break

        current_frame_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(prev_frame_gray, current_frame_gray)
        non_zero_count = cv2.countNonZero(frame_diff)

        if non_zero_count > 10000:  # Adjust threshold for scene change sensitivity
            scenes.append(frame_count)

        prev_frame_gray = current_frame_gray
        frame_count += 1

    cap.release()
    logging.info(f"{Color.INFO}Detected {len(scenes)} scenes in the video.")
    return scenes


def create_shorts_from_segments(min_duration=25, max_duration=60, min_clips=4, max_clips=10):
    """Create YouTube Shorts from video files in the current directory."""
    shorts_created = []
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.webm'))]

    for video_file in video_files:
        logging.info(f"{Color.INFO}Processing video for shorts: {video_file}{Color.RESET}")
        try:
            with VideoFileClip(video_file) as clip:
                total_duration = clip.duration
                if total_duration < min_duration:
                    logging.warning(
                        f"{Color.WARNING}Video {video_file} is shorter than the minimum duration for shorts. Skipping.{Color.RESET}")
                    continue

                # Detect scenes and create shorts
                scenes = detect_scenes(video_file)
                if len(scenes) < 2:
                    logging.warning(
                        f"{Color.WARNING}Not enough scenes detected to create shorts from {video_file}. Skipping.{Color.RESET}")
                    continue

                existing_shorts = set(os.path.splitext(f)[0] for f in os.listdir('.') if f.startswith("short_"))
                shorts_to_create = random.randint(min_clips, max_clips)  # Create between min_clips and max_clips
                created_this_video = 0

                # Ensure we create shorts from different sections of the video
                used_time_ranges = []

                while created_this_video < shorts_to_create:
                    start_scene = random.choice(scenes[:-1])  # Ensure we don't go out of bounds
                    end_scene = random.choice(scenes[1:])  # Ensure end_scene is after start_scene
                    if end_scene <= start_scene:
                        continue

                    start_time = start_scene / clip.fps
                    end_time = end_scene / clip.fps
                    clip_duration = end_time - start_time

                    if min_duration <= clip_duration <= max_duration:
                        time_range = (start_time, end_time)

                        # Check if this time range has been used before
                        if time_range not in used_time_ranges:
                            output_file = f"short_{os.path.splitext(os.path.basename(video_file))[0]}_{created_this_video + 1}.mp4"

                            # Ensure the short does not already exist
                            if output_file not in existing_shorts:
                                short_clip = clip.subclip(start_time, end_time)
                                short_clip = short_clip.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
                                short_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
                                logging.info(
                                    f"{Color.INFO}Created short clip: {output_file} from {start_time:.2f} to {end_time:.2f}{Color.RESET}")
                                shorts_created.append(output_file)
                                created_this_video += 1
                                used_time_ranges.append(time_range)  # Mark this time range as used
                            else:
                                logging.warning(
                                    f"{Color.WARNING}Short already exists: {output_file}. Skipping.{Color.RESET}")
                        else:
                            logging.warning(
                                f"{Color.WARNING}Time range {time_range} has already been used. Skipping this clip.{Color.RESET}")
                    else:
                        logging.warning(
                            f"{Color.WARNING}Generated clip duration is not within the specified range: {clip_duration:.2f} seconds. Skipping.{Color.RESET}")
        except Exception as e:
            logging.error(f"{Color.ERROR}Error processing video {video_file}: {e}{Color.RESET}")

    return shorts_created


def main(video_urls=None, create_shorts=False, min_clips=4, max_clips=10):
    if create_shorts:
        create_shorts_from_segments(min_clips=min_clips, max_clips=max_clips)
    elif video_urls:
        for url in video_urls:
            video_file = download_video(url)
            if video_file:
                debug_video_properties(video_file)
                split_video(video_file)


def read_links_from_file(file_path):
    """Read video URLs from a text file."""
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        logging.info(f"{Color.INFO}Read {len(urls)} URLs from {file_path}{Color.RESET}")
        return urls
    except Exception as e:
        logging.error(f"{Color.ERROR}Error reading URLs from file: {e}{Color.RESET}")
        return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download YouTube videos, split them into segments, and create shorts.")
    parser.add_argument('--url_file', type=str, help="Path to the text file containing video URLs.")
    parser.add_argument('--create_shorts', action='store_true',
                        help="Create shorts from videos in the current directory.")
    parser.add_argument('--min_clips', type=int, default=4, help="Minimum number of shorts to create.")
    parser.add_argument('--max_clips', type=int, default=10, help="Maximum number of shorts to create.")

    args = parser.parse_args()

    if args.url_file:
        video_urls = read_links_from_file(args.url_file)
        main(video_urls=video_urls)
    if args.create_shorts:
        main(create_shorts=True, min_clips=args.min_clips, max_clips=args.max_clips)