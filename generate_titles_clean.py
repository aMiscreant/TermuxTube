#!/usr/bin/env python3
import os
import subprocess
import json
import re

WHISPER_BIN = os.path.expanduser("~/whisper.cpp/build/bin/whisper-cli")
WHISPER_MODEL = os.path.expanduser("~/whisper.cpp/models/ggml-base.bin")

PROFANITY_LIST = [
    "fuck", "fucking", "shit", "bitch", "asshole", "dick", "pussy",
    "bastard", "damn", "hell", "nigger", "retard", "cunt"
]

def remove_profanity(text):
    # Remove bad words from the text completely
    for word in PROFANITY_LIST:
        pattern = rf"\b{re.escape(word)}\b"
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    # Clean up extra spaces and punctuation
    text = re.sub(r"\s{2,}", " ", text).strip()
    text = re.sub(r"^[^\w]+|[^\w]+$", "", text)
    return text

def extract_audio_snippet(video_path, wav_path):
    try:
        subprocess.run([
            "ffmpeg", "-i", video_path,
            "-t", "10", "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            wav_path, "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return os.path.exists(wav_path)
    except Exception as e:
        print(f"[!] ffmpeg error: {e}")
        return False

def whisper_transcribe(wav_path):
    try:
        subprocess.run([
            WHISPER_BIN,
            "-m", WHISPER_MODEL,
            "-f", wav_path,
            "-otxt",
            "-of", wav_path[:-4]
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        txt_path = wav_path[:-4] + ".txt"
        if os.path.exists(txt_path):
            with open(txt_path, "r") as f:
                return f.read().strip()
    except Exception as e:
        print(f"[!] Whisper error: {e}")
    return ""

def is_valid_whisper(text):
    if not text or len(text) < 8:
        return False
    if len(text.split()) < 3:
        return False
    if re.search(r"[^a-zA-Z0-9\s.,!?'\"]", text):
        return False
    return True

def fallback_title(filename):
    name = os.path.splitext(filename)[0]
    match = re.search(r"Experience\s+#(\d+)\s+-\s+(.+?)_part_(\d+)_(\d+)", name)
    if match:
        episode = match.group(1)
        guest = match.group(2).replace("_", " ").strip()
        part = f"{match.group(3)}-{match.group(4)}"
        return f"{guest} - Joe Rogan Experience #{episode} (Part {part})"
    else:
        return name.replace("_", " ").title()

def generate_titles(folder_path):
    print(f"[+] Scanning folder: {folder_path}")
    titles = {}
    whisper_fail_log = []

    for file in os.listdir(folder_path):
        if not file.lower().endswith(".mp4"):
            continue

        video_path = os.path.join(folder_path, file)
        base = os.path.splitext(file)[0]
        tmp_wav = os.path.join(folder_path, f"{base}_tmp.wav")

        print(f"    → Processing: {file}")

        if extract_audio_snippet(video_path, tmp_wav):
            text = whisper_transcribe(tmp_wav)
            os.remove(tmp_wav)
            txt_output = tmp_wav.replace(".wav", ".txt")
            if os.path.exists(txt_output):
                os.remove(txt_output)

            if is_valid_whisper(text):
                raw_title = text.splitlines()[0].strip().title()
                clean_title = remove_profanity(raw_title)
                print(f"      ↪ Whisper Title: {clean_title}")
                title = clean_title
            else:
                title = fallback_title(file)
                print(f"      ↪ Fallback Title: {title}")
                if text:
                    whisper_fail_log.append(f"{file}: {text}")
        else:
            title = fallback_title(file)
            print(f"      ↪ ffmpeg failed, using fallback.")
            whisper_fail_log.append(f"{file}: [ffmpeg failed]")

        titles[file] = title

    # Save titles
    out_path = os.path.join(folder_path, "titles.json")
    with open(out_path, "w") as f:
        json.dump(titles, f, indent=2)
    print(f"[✓] Titles saved: {out_path}")

    # Save Whisper failures
    if whisper_fail_log:
        fail_log = os.path.join(folder_path, "whisper_failures.txt")
        with open(fail_log, "w") as f:
            f.write("\n\n".join(whisper_fail_log))
        print(f"[!] Issues logged to: {fail_log}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_titles_whisper.py /path/to/Shorts/JRE")
        exit(1)
    folder = sys.argv[1]
    if not os.path.exists(folder):
        print(f"[!] Folder not found: {folder}")
        exit(1)
    generate_titles(folder)
