import asyncio
import os
import glob
import yt_dlp
import instaloader
import logging

DOWNLOAD_DIR = "downloads"
MAX_SIZE = 50 * 1024 * 1024  # 50MB

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_file_size(path):
    return os.path.getsize(path) if os.path.exists(path) else 0


async def download_media(url: str) -> dict:
    if "instagram.com" in url:
        return await asyncio.to_thread(download_instagram, url)
    elif "youtube.com" in url or "youtu.be" in url:
        return await asyncio.to_thread(download_youtube, url)
    elif "tiktok.com" in url:
        return await asyncio.to_thread(download_tiktok, url)
    else:
        return {"type": "error", "error": "Qo'llab-quvvatlanmaydigan havola!"}


def download_youtube(url: str) -> dict:
    try:
        # Avval video ma'lumotlarini olamiz
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "video")[:50]

        # Musiqa havolasimi yoki video?
        is_music = any(x in url.lower() for x in ["music.youtube", "playlist"])

        if is_music:
            return download_youtube_audio(url, title)
        else:
            return download_youtube_video(url, title)

    except Exception as e:
        logging.error(f"YouTube xatolik: {e}")
        return {"type": "error", "error": f"YouTube yuklab bo'lmadi: {str(e)[:100]}"}


def download_youtube_video(url: str, title: str) -> dict:
    output_template = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "best[filesize<50M]/best[height<=720]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "")

        # Faylni topamiz
        files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{video_id}.*"))
        if not files:
            return {"type": "error", "error": "Fayl topilmadi"}

        filepath = files[0]

        if get_file_size(filepath) > MAX_SIZE:
            os.remove(filepath)
            return {"type": "error", "error": "Fayl 50MB dan katta! Qisqaroq video sinab ko'ring."}

        return {"type": "video", "path": filepath, "title": title}

    except Exception as e:
        return {"type": "error", "error": f"Video yuklab bo'lmadi: {str(e)[:100]}"}


def download_youtube_audio(url: str, title: str) -> dict:
    output_template = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "")

        files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{video_id}.*"))
        if not files:
            return {"type": "error", "error": "Audio fayl topilmadi"}

        filepath = files[0]

        if get_file_size(filepath) > MAX_SIZE:
            os.remove(filepath)
            return {"type": "error", "error": "Fayl 50MB dan katta!"}

        return {"type": "audio", "path": filepath, "title": title}

    except Exception as e:
        return {"type": "error", "error": f"Audio yuklab bo'lmadi: {str(e)[:100]}"}


def download_instagram(url: str) -> dict:
    try:
        loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            quiet=True,
            dirname_pattern=DOWNLOAD_DIR
        )

        # Shortcode olish
        shortcode = extract_instagram_shortcode(url)
        if not shortcode:
            return {"type": "error", "error": "Instagram havolasi noto'g'ri"}

        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Video postmi?
        if post.is_video:
            # yt-dlp orqali yuklaymiz (tezroq)
            return download_with_ytdlp(url, "video")

        # Bir nechta rasm?
        if post.typename == "GraphSidecar":
            paths = []
            for i, node in enumerate(post.get_sidecar_nodes()):
                if node.is_video:
                    continue  # Videolarni o'tkazib yuboramiz
                filepath = os.path.join(DOWNLOAD_DIR, f"insta_{shortcode}_{i}.jpg")
                loader.download_pic(filepath, node.display_url, post.date_utc)
                if os.path.exists(filepath):
                    paths.append(filepath)

            if paths:
                return {"type": "multiple_photos", "paths": paths}

        # Oddiy rasm
        filepath = os.path.join(DOWNLOAD_DIR, f"insta_{shortcode}.jpg")
        loader.download_pic(filepath, post.url, post.date_utc)

        if os.path.exists(filepath):
            return {"type": "photo", "path": filepath}
        else:
            return {"type": "error", "error": "Rasm yuklab bo'lmadi"}

    except Exception as e:
        logging.error(f"Instagram xatolik: {e}")
        # Fallback: yt-dlp bilan urinib ko'ramiz
        return download_with_ytdlp(url, "video")


def download_tiktok(url: str) -> dict:
    return download_with_ytdlp(url, "video")


def download_with_ytdlp(url: str, media_type: str = "video") -> dict:
    output_template = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "best[filesize<50M]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "unknown")
            title = info.get("title", "")[:50]

        files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{video_id}.*"))
        if not files:
            return {"type": "error", "error": "Fayl topilmadi"}

        filepath = files[0]

        if get_file_size(filepath) > MAX_SIZE:
            os.remove(filepath)
            return {"type": "error", "error": "Fayl 50MB dan katta!"}

        return {"type": media_type, "path": filepath, "title": title}

    except Exception as e:
        return {"type": "error", "error": f"Yuklab bo'lmadi: {str(e)[:100]}"}


def extract_instagram_shortcode(url: str) -> str:
    import re
    patterns = [
        r"instagram\.com/p/([A-Za-z0-9_-]+)",
        r"instagram\.com/reel/([A-Za-z0-9_-]+)",
        r"instagram\.com/tv/([A-Za-z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""
