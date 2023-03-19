import re, requests, json
from bs4 import BeautifulSoup
from enum import Enum
from typing import Tuple, List, Dict, Any


def _get_api_key(response) -> str:
    soup = BeautifulSoup(response, "html.parser")
    key = None
    for script_tag in soup.find_all("script"):
        script = script_tag.string
        if script is not None:
            match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', script)
            if match is not None:
                key = match.group(1)
                break
    assert key is not None
    return key


def _get_watch_api_key(ytb_id: str) -> str:
    session = requests.Session()
    response = session.get(
        "https://www.youtube.com/watch",
        params={"v": ytb_id},
    ).content.decode()
    return _get_api_key(response)


def _get_streaming_data(ytb_id: str, api_key: str) -> dict:
    post_data = {
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "16.05",
            },
        },
        "videoId": ytb_id,
    }
    session = requests.Session()
    return json.loads(
        session.post(
            "https://www.youtube.com/youtubei/v1/player",
            params={"key": api_key},
            data=json.dumps(post_data),
        ).content
    )


class YtbInfo(Enum):
    Title = "title"
    VideoId = "videoId"
    KeyWords = "keyWords"
    Author = "author"


CODECS = re.compile(r"codecs=\"(.*)\"")


class YtbUrlData:
    def __init__(self, ytb_id) -> None:
        key = _get_watch_api_key(ytb_id)
        self._data = _get_streaming_data(ytb_id, key)
        with open("sample.json", mode="w") as fp:
            json.dump(self._data, fp, indent=4, ensure_ascii=False)


def _get_info(data: dict, info: YtbInfo) -> str:
    return data.get("videoDetails", {}).get(info.value, "")


def _get_audio_url(data: dict) -> Tuple[str, str]:
    formats: List[Dict[str, Any]] = sorted(
        data["streamingData"]["adaptiveFormats"],
        key=lambda x: x.get("bitrate", -1),
        reverse=True,
    )
        
    for f in formats:
        if f.get("mimeType", "").startswith("audio"):
            if matched := re.search(CODECS, f.get("mimeType", "")):
                codecs = matched.groups()[0]
            else:
                codecs = ""
            content_length = int(f.get("contentLength", "10_000_000"))
            return f.get("url", "") + f"&range=0-{content_length}", codecs
    return "", ""


def get_ytb_audio(url_data: YtbUrlData) -> Tuple[str, str]:
    """return audio url and codecs"""
    return _get_audio_url(url_data._data)


def get_ytb_info(url_data: YtbUrlData, info: YtbInfo) -> str:
    return _get_info(url_data._data, info)


def get_ytb_cover(url_data: YtbUrlData) -> str:
    return ""
