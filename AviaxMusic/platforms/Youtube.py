
import os
import re
import json
import yt_dlp
import random
import asyncio
from typing import Union
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
from AviaxMusic.utils.database import is_on_off
from AviaxMusic.utils.formatters import time_to_seconds

# ---------------------------------------------------------------------------------
#  Cookie Management
# ---------------------------------------------------------------------------------

def cookie_txt_file():
    """
    Locates the cookie file in the 'cookies' folder in the root directory.
    Matches the structure shown in your GitHub screenshot.
    """
    # os.getcwd() gets the folder where you run the bot (root)
    cookie_dir = os.path.join(os.getcwd(), "cookies")
    
    if not os.path.exists(cookie_dir):
        return None
    
    # Find all .txt files in that folder
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        return None
        
    # Pick a random one (useful if you have multiple cookie files)
    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file

# ---------------------------------------------------------------------------------
#  Helper Functions
# ---------------------------------------------------------------------------------

async def check_file_size(link):
    async def get_format_info(link):
        cookie_file = cookie_txt_file()
        if not cookie_file:
            print("No cookies found. Cannot check file size.")
            return None
            
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

# ---------------------------------------------------------------------------------
#  Main YouTubeAPI Class
# ---------------------------------------------------------------------------------

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        umm = text[offset : offset + length]
        if "?si=" in umm:
            umm = umm.split("?si=")[0]
        return umm

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Pure Cookie/yt-dlp logic for getting stream URL
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return 0, "No cookies found. Cannot download video."
            
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        try:
            plist = await Playlist.get(link)
        except:
            return []

        videos = plist.get("videos") or []
        ids: list[str] = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return [], link
            
        ytdl_opts = {"quiet": True, "cookiefile" : cookie_file}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        
        loop = asyncio.get_running_loop()

        def audio_dl():
            cookie_file = cookie_txt_file()
            # Try to download even without cookies if necessary, but warn
            ydl_opts_audio = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile" : cookie_file,
                "no_warnings": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                info = ydl.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.mp3")
                if os.path.exists(xyz):
                    return xyz
                ydl.download([link])
                return xyz

        def video_dl():
            cookie_file = cookie_txt_file()
            ydl_opts_video = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile" : cookie_file,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                info = ydl.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.mp4")
                if os.path.exists(xyz):
                    return xyz
                ydl.download([link])
                return xyz

        def song_specific_dl(is_video=False):
            cookie_file = cookie_txt_file()
            
            if is_video:
                formats = f"{format_id}+140" if format_id else "bestvideo+bestaudio"
            else:
                formats = format_id if format_id else "bestaudio"

            fpath_out = f"downloads/{title}" if title else "downloads/%(id)s.%(ext)s"

            ydl_opts = {
                "format": formats,
                "outtmpl": fpath_out,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile" : cookie_file,
                "prefer_ffmpeg": True,
            }

            if is_video:
                ydl_opts["merge_output_format"] = "mp4"
            else:
                 ydl_opts["postprocessors"] = [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

        # Logic Flow
        downloaded_file = None
        direct = False

        if songvideo:
            await loop.run_in_executor(None, lambda: song_specific_dl(is_video=True))
            # Fallback for path return if song specific name not tracked perfectly here
            downloaded_file = await loop.run_in_executor(None, video_dl)
            direct = True

        elif songaudio:
            downloaded_file = await loop.run_in_executor(None, audio_dl)
            direct = True

        elif video:
            cookie_file = cookie_txt_file()
            force_download = await is_on_off(1)
            
            if force_download:
                direct = True
                downloaded_file = await loop.run_in_executor(None, video_dl)
            else:
                try:
                    if not cookie_file:
                        # If no cookies, just try DL
                        raise Exception("No Cookies")
                    
                    proc = await asyncio.create_subprocess_exec(
                        "yt-dlp",
                        "--cookies", cookie_file,
                        "-g",
                        "-f", "best[height<=?720][width<=?1280]",
                        f"{link}",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, stderr = await proc.communicate()
                    if stdout:
                        downloaded_file = stdout.decode().split("\n")[0]
                        direct = False
                    else:
                        file_size = await check_file_size(link)
                        if file_size:
                            total_size_mb = file_size / (1024 * 1024)
                            if total_size_mb <= 250:
                                downloaded_file = await loop.run_in_executor(None, video_dl)
                                direct = True
                except:
                     downloaded_file = await loop.run_in_executor(None, video_dl)
                     direct = True
        else:
            downloaded_file = await loop.run_in_executor(None, audio_dl)
            direct = True

        return downloaded_file, direct

