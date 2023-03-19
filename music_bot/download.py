import os, subprocess, time, re
from typing import Tuple
from enum import Enum

import youtube_dl, requests
from mutagen.mp4 import MP4

from .process_ytb_url import YtbUrlData, YtbInfo, get_ytb_audio, get_ytb_info
from .process_bil_url import BilUrlData, get_bil_audio, get_bil_author, get_bil_title
from .error import UnknownPlatformError

CODECS_EXT = {"opus": "opus", "mp4a.40.5": "m4a", "mp4a.40.2": "m4a"}
YTB_URL = re.compile(
    r"((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)
BIL_URL = re.compile(
    r"((?:https?:)?\/\/)?((?:www)\.)?((?:bilibili\.com|b23.tv))(\/video)?\/((?:[\w\-]+))(\/?\?)?(\S+)?$"
)
SC_URL = re.compile(r"(https?:\/\/)?(www.)?(m\.)?soundcloud\.com\/[\w\-\.]+(\/)+[\w\-\.]+/?$")


class Platform(Enum):
    Ytb = "Youtube"
    Bil = "Bilibili"
    SC = "SoundCloud"
    Unknown = "Unknown"
    


URL = {Platform.Ytb: YTB_URL, Platform.Bil: BIL_URL, Platform.SC: SC_URL}


def detect_url(text: str) -> Tuple[str, Platform]:
    """return url id and platform"""
    for platform, pattern in URL.items():
        if matched := re.search(pattern, text):
            if platform == Platform.SC:
                return matched.group(), platform
            return matched.groups()[4], platform
    return "", Platform.Unknown


def convert_to_m4a(file: str, del_original: bool = False) -> str:
    converted = f"{os.path.splitext(file)[0]}.m4a"
    process = subprocess.Popen(["ffmpeg", "-y", "-i", file, converted])
    while process.poll() is None:
        continue
    if del_original:
        os.remove(file)
    return converted


def set_tag(file: str, params: dict):
    song = MP4(file)
    for key, value in params.items():
        song[key] = value
    song.save()


def download_ytb_audio(ytb_id: str) -> str:
    """return file name, and converted to m4a"""
    data = YtbUrlData(ytb_id)
    url, codecs = get_ytb_audio(data)
    ext = CODECS_EXT.get(codecs, "")
    title = get_ytb_info(data, YtbInfo.Title).replace("/", "／")
    file_name = f"{title}.{ext}"
    params = {"outtmpl": file_name}
    with youtube_dl.YoutubeDL(params) as ytl:
        ytl.download([url])

    if ext != "m4a":
        print(f"{file_name=}, {codecs=}")
        file_name = convert_to_m4a(file_name, del_original=True)

    tags = {
        "track title": title,
        "artist": [get_ytb_info(data, YtbInfo.Author)],
        "album artist": get_ytb_info(data, YtbInfo.KeyWords),
    }
    set_tag(file_name, tags)

    return file_name


def download_bil_audio(bil_id: str) -> str:
    data = BilUrlData(bil_id)
    url, codecs = get_bil_audio(data)
    ext = CODECS_EXT.get(codecs, "")
    title = get_bil_title(data)
    author = get_bil_author(data)
    file_name = f"{title}.{ext}"

    print(f"start downloading file {file_name}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "referer": "https://www.bilibili.com",
    }
    response = requests.get(url, headers=headers)

    file_size = int(response.headers["content-length"]) / 1024 / 1024
    chunk_size = 1024

    print(f"file size: {file_size}")
    start_time = time.time()
    with open(file_name, mode="wb") as fp:
        for chunk in response.iter_content(chunk_size=chunk_size):
            fp.write(chunk)
    end_time = time.time()

    print(f"total time: {end_time-start_time:0.2f}s")

    if ext != "m4a":
        print(f"{file_name=}, {codecs=}")
        file_name = convert_to_m4a(file_name, True)

    tags = {"track title": title, "artist": [author]}
    set_tag(file_name, tags)

    return file_name

def download_sc_video(sc_url: str) -> str:
    """return file name"""
    return ""


DOWNLOAD_Func = {
    Platform.Ytb: download_ytb_audio,
    Platform.Bil: download_bil_audio,
}


def download_audio(id: str, platform: Platform) -> str:
    """return file name"""
    return DOWNLOAD_Func[platform](id)
