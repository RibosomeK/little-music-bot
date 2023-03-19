import re, requests, json
from typing import Tuple

BIL_URL = re.compile(
    r"((?:https?:)?\/\/)?((?:www)\.)?((?:bilibili\.com|b23.tv))(\/video|audio)?\/((?:[\w\-]+))\/?\?(\S+)?$"
)


def _reform_url(bil_id: str) -> str:
    if bil_id.startswith("BV") or bil_id.startswith("av"):
        return f"https://www.bilibili.com/video/{bil_id}"
    elif bil_id.startswith("au"):
        return f"https://www.bilibili.com/audio/{bil_id}"
    else:
        return f"https://b23.tv/{bil_id}"


class BilUrlData:
    def __init__(self, bil_id: str) -> None:
        url = _reform_url(bil_id)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
            "referer": "https://www.bilibili.com",
        }

        response = requests.get(url, headers=headers)
        self.play_info = json.loads(
            re.findall(r"<script>window.__playinfo__=(.*?)</script>", response.text)[0]
        )["data"]["dash"]
        self.video_info = json.loads(
            re.findall(
                r"<script>window.__INITIAL_STATE__=(.*?)</script>", response.text
            )[0].split(";(function(){")[0]
        )


def get_bil_title(bil_url_data: BilUrlData) -> str:
    return bil_url_data.video_info["videoData"]["title"].replace("/", "／")


def get_bil_author(bil_url_data: BilUrlData) -> str:
    return bil_url_data.video_info["videoData"]["owner"]["name"].replace("/", "／")


def get_bil_audio(bil_url_data: BilUrlData) -> Tuple[str, str]:
    audios = sorted(
        bil_url_data.play_info["audio"], key=lambda x: x["bandwidth"], reverse=True
    )
    return audios[0]["base_url"], audios[0]["codecs"]
