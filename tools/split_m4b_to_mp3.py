import subprocess
import json
import os
import re
from collections import defaultdict
from natsort import natsorted

# Input M4B file and output directory
input_dir = input("Enter the directory containing M4B file(s): ").strip('"')
base_output_dir = input("Enter the base output directory: ").strip('"')


def sanitize_filename(filename):
    """Sanitize filenames to remove characters that might be invalid for the filesystem."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def get_metadata(input_file):
    """Extract metadata and chapter information using ffprobe."""
    cmd = [
        "ffprobe",
        "-loglevel", "error",
        "-print_format", "json",
        "-show_format",
        "-show_chapters",
        "-i", input_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)


def convert_chapter(input_file, output_file, start_time, end_time, chapter_title, album_title, track_number):
    """Convert a chapter to MP3 and add metadata using ffmpeg."""
    cmd = [
        "ffmpeg",
        "-loglevel", "error",
        "-i", input_file,
        "-ss", start_time,
        "-to", end_time,
        "-metadata", f"title={chapter_title}",
        "-metadata", f"album={album_title}",
        "-metadata", f"track={track_number}",
        "-acodec", "libmp3lame",
        "-ar", "22050",
        "-b:a", "40k",
        "-ac", "1",
        output_file
    ]
    subprocess.run(cmd)


def group_m4b_files(directory):
    """Group M4B files by their audiobook title, ignoring part numbers."""
    file_groups = defaultdict(list)
    for filename in os.listdir(directory):
        if filename.endswith(".m4b"):
            # Adjust this pattern based on your filenames
            match = re.match(r"(\d+)?\s?(.+)\.m4b", filename)
            if match:
                key = match.group(2)  # Group by the audiobook title
                file_groups[key].append(os.path.join(directory, filename))
    for key in file_groups:
        file_groups[key] = natsorted(file_groups[key])  # Natural sort
    return file_groups


def process_audiobook_group(group_files, output_dir):
    """Convert a group of M4B files into chapters, maintaining continuous track numbering."""
    track_number = 1
    for input_file in group_files:
        metadata = get_metadata(input_file)
        album_title = sanitize_filename(metadata['format'].get('tags', {}).get('album', 'Unknown Album'))
        chapters = metadata['chapters']

        print(f"\nProcessing: {input_file}...")
        for chapter in chapters:
            title = sanitize_filename(chapter.get('tags', {}).get('title', f'Chapter {track_number}'))
            start_time = chapter['start_time']
            end_time = chapter['end_time']
            output_file = os.path.join(output_dir, f"{track_number} {title}.mp3")
            print(f"Converting chapter {track_number}: {title}...")
            convert_chapter(input_file, output_file, start_time, end_time, title, album_title, track_number)
            track_number += 1
    print(f"Conversion completed for audiobook in: {output_dir}")


def main():
    audiobook_groups = group_m4b_files(input_dir)
    for album_title, group_files in audiobook_groups.items():
        output_dir = os.path.join(base_output_dir, sanitize_filename(album_title))
        os.makedirs(output_dir, exist_ok=True)
        process_audiobook_group(group_files, output_dir)


if __name__ == "__main__":
    main()
