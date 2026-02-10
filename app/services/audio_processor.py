
import os
import yt_dlp
import ffmpeg
from app.core.config import settings

def download_youtube_audio(url: str, output_id: str) -> str:
    """Downloads audio from a YouTube URL using yt-dlp."""
    output_path = os.path.join(settings.AUDIO_DIR, f"{output_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # ydl changes extension to mp3 after postprocessing
        final_path = os.path.splitext(filename)[0] + ".mp3"
        return final_path, info.get('title', 'Unknown Video')

def extract_audio_from_file(video_path: str, output_id: str) -> str:
    """Extracts audio from a local video file using ffmpeg."""
    output_path = os.path.join(settings.AUDIO_DIR, f"{output_id}.mp3")
    
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_path, acodec='mp3', audio_bitrate='192k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
        raise e
