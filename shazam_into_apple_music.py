import os
import asyncio
from shazamio import Shazam
from mutagen.easyid3 import EasyID3
import subprocess

async def identify_and_rename(folder_path):
    shazam = Shazam()
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3"):
            audio_file = os.path.join(folder_path, filename)
            print(f"Processing: {filename}")
            try:
                # Open the file as binary data
                with open(audio_file, "rb") as f:
                    file_data = f.read()

                # Recognize song from binary data
                result = await shazam.recognize(file_data)

                # Extract song title and artist
                track = result.get('track', {})
                title = track.get('title', 'Unknown Title')
                artist = track.get('subtitle', 'Unknown Artist')
                album = track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown Album')

                # Generate the new file name
                new_filename = f"{artist} - {title}.mp3"
                new_file_path = os.path.join(folder_path, new_filename)

                # Update MP3 metadata
                audio = EasyID3(audio_file)
                audio['title'] = title
                audio['artist'] = artist
                audio['album'] = album
                audio.save()

                # Rename the file
                os.rename(audio_file, new_file_path)
                print(f"Renamed to: {new_filename}")

                # Import into Apple Music
                import_into_apple_music(new_file_path)
                print(f"Imported {new_filename} into Apple Music")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def import_into_apple_music(file_path):
    """
    Use AppleScript to add the song to the Apple Music library.
    """
    applescript = f'''
    tell application "Music"
        add POSIX file "{file_path}" to library playlist 1
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", applescript], check=True)
        print(f"Successfully added {file_path} to Apple Music.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add {file_path} to Apple Music: {e}")

# Get folder path from user
folder_path = input("Enter the folder path containing MP3 files: ")
if os.path.exists(folder_path):
    asyncio.run(identify_and_rename(folder_path))
else:
    print("Invalid folder path. Please try again.")
