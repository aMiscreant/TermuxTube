import os
import logging
from moviepy import VideoFileClip
import argparse

# ANSI escape codes for colored output
class Color:
    INFO = "\033[92m"  # Green
    WARNING = "\033[93m"  # Yellow
    ERROR = "\033[91m"  # Red
    RESET = "\033[0m"  # Reset to default


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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


def main(video_file, max_duration):
    split_video(video_file, max_duration)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a video into segments.")
    parser.add_argument('--video_file', type=str, required=True, help="Path to the video file to split.")
    parser.add_argument('--max_duration', type=int, default=600, help="Maximum duration of each segment in seconds.")

    args = parser.parse_args()
    main(args.video_file, args.max_duration)