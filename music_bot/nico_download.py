import requests, json, html, re, logging, http.client, threading, os
from typing import Tuple, Optional, Dict, List, Any

from .error import try_if_no_exceptions

LOGIN_URl = "https://account.nicovideo.jp/api/v1/login"
SESSION_URL = "https://api.dmc.nico/api/sessions"
WATCH_URL = "https://www.nicovideo.jp/watch"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "referer": "https://www.nicovideo.jp",
}

Account, Password = str, str
LoginInfo = Tuple[Account, Password]

http.client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def login_nico(login_info: LoginInfo) -> requests.Session:
    session = requests.Session()
    params = {
        "url": LOGIN_URl,
        "params": {"site": "niconico"},
        "data": {"mail_tel": login_info[0], "password": login_info[1]},
        "allow_redirects": False,
    }
    try_if_no_exceptions(session.post, params, {requests.exceptions.SSLError})
    return session


class NicoUrlData:
    def __init__(
        self, nico_id: str, session: Optional[requests.Session] = None
    ) -> None:
        self.session = session if session is not None else requests.Session()
        self.info_data = self.get_nico_info(nico_id, self.session)

    @staticmethod
    def get_nico_info(
        nico_id: str, session: Optional[requests.Session] = None
    ) -> Dict[str, Any]:
        """return data-api-data info, recommend to pass a session that already login"""
        if session is None:
            session = requests.Session()
        response = session.get(f"{WATCH_URL}/{nico_id}")
        return json.loads(
            html.unescape(re.findall(r'data-api-data="(.+?)"', response.text)[0])
        )


def get_nico_title(nico_url_data: NicoUrlData) -> str:
    return nico_url_data.info_data["video"]["title"]


def get_nico_author(nico_url_data: NicoUrlData) -> str:
    return nico_url_data.info_data["owner"]["nickname"]


def get_nico_tags(nico_url_data: NicoUrlData) -> List[str]:
    return [tag["name"] for tag in nico_url_data.info_data["tags"]["items"]]


def get_nico_description(nico_url_data: NicoUrlData) -> str:
    return nico_url_data.info_data["video"]["descriptions"]


def is_premium(nico_url_data: NicoUrlData) -> bool:
    if nico_url_data.info_data["viewer"] is None:
        return False
    return nico_url_data.info_data["viewer"]["isPremium"]


def get_nico_thumbnail(nico_url_data: NicoUrlData) -> str:
    """return thumbnail url in best quality"""
    qualities = ("largeUrl", "middleUrl", "url")
    for quality in qualities:
        if (url := nico_url_data.info_data["video"]["thumbnail"][quality]) is not None:
            return url
    return ""


def get_download_link(nico_url_data: NicoUrlData) -> str:
    """return download link with given nico info data"""
    nico_info = nico_url_data.info_data

    recipe_id = nico_info["media"]["delivery"]["recipeId"]
    content_id = nico_info["media"]["delivery"]["movie"]["contentId"]
    video_src_ids = nico_info["media"]["delivery"]["movie"]["session"]["videos"]
    audio_src_ids = nico_info["media"]["delivery"]["movie"]["session"]["audios"]
    lifetime = nico_info["media"]["delivery"]["movie"]["session"]["heartbeatLifetime"]

    try:
        is_premium = nico_info["viewer"]["isPremium"]
    except TypeError:
        is_premium = False
    token_json = nico_info["media"]["delivery"]["movie"]["session"]["token"]
    token = json.loads(token_json)

    if is_premium:
        # not tested for lack of premium account
        try:
            transfer_preset = token["transfer_presets"][0]
            storyboard = nico_info["media"]["delivery"]["storyboard"]
            player_id = storyboard["playerId"]
            auth_type = storyboard["authTypes"]["storyboard"]
        except KeyError:
            transfer_preset = token["transfer_presets"][0]
            player_id = nico_info["media"]["delivery"]["movie"]["session"]["playerId"]
            auth_type = "ht2"
    else:
        transfer_preset = ""
        player_id = nico_info["media"]["delivery"]["movie"]["session"]["playerId"]
        auth_type = "ht2"

    signature = nico_info["media"]["delivery"]["movie"]["session"]["signature"]
    content_key_timeout = nico_info["media"]["delivery"]["movie"]["session"][
        "contentKeyTimeout"
    ]

    service_id = token["service_id"]
    service_user_id = token["service_user_id"]
    priority = token["priority"]

    response = nico_url_data.session.post(
        headers=HEADERS,
        url=SESSION_URL,
        params={"_format": "json"},
        json={
            "session": {
                "recipe_id": recipe_id,
                "content_id": content_id,
                "content_type": "movie",
                "content_src_id_sets": [
                    {
                        "content_src_ids": [
                            {
                                "src_id_to_mux": {
                                    "video_src_ids": video_src_ids,
                                    "audio_src_ids": audio_src_ids,
                                }
                            }
                        ]
                    }
                ],
                "timing_constraint": "unlimited",
                "keep_method": {"heartbeat": {"lifetime": lifetime}},
                "protocol": {
                    "name": "http",
                    "parameters": {
                        "http_parameters": {
                            "parameters": {
                                "http_output_download_parameters": {
                                    "use_well_known_port": "yes",
                                    "use_ssl": "yes",
                                    "transfer_preset": transfer_preset,
                                }
                            }
                        }
                    },
                },
                "content_uri": "",
                "session_operation_auth": {
                    "session_operation_auth_by_signature": {
                        "token": token_json,
                        "signature": signature,
                    }
                },
                "content_auth": {
                    "auth_type": auth_type,
                    "content_key_timeout": content_key_timeout,
                    "service_id": service_id,
                    "service_user_id": service_user_id,
                },
                "client_info": {"player_id": player_id},
                "priority": priority,
            }
        },
    )
    response_code = response.status_code
    if response_code in [200, 201]:
        response_json = response.json()
        with open("./tests/response.json", mode="w") as fp:
            json.dump(response_json, fp, ensure_ascii=False, indent=4)
        content_uri = response_json["data"]["session"]["content_uri"]
        return content_uri
    elif response_code in [403, 400]:
        raise requests.exceptions.HTTPError(f"{response_code} error: {response.text}")
    else:
        raise requests.exceptions.HTTPError(f"Unknown error: {response.text}")


def download_nico_video(
    nico_url_data: NicoUrlData, output_dir: str = "./", num_of_thread: int = 50
) -> str:
    """download video, return file name"""
    content_link = get_download_link(nico_url_data)
    title = get_nico_title(nico_url_data)

    content_response = nico_url_data.session.head(content_link)
    file_size = int(content_response.headers["content-length"])
    ext = content_response.headers["content-type"].split("/")[-1]

    file_name = f"{title}.{ext}"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "wb") as fp:
        fp.truncate(file_size)

    chunk_size = (file_size // num_of_thread) + 1

    def handler(
        session: requests.Session, start: int, end: int, video_url: str, file_path: str
    ):
        headers = {"Range": "bytes=%d-%d" % (start, end)}
        params = {"url": video_url, "headers": headers, "stream": True}
        res = try_if_no_exceptions(
            session.get, params, {requests.exceptions.ConnectionError}
        )
        with open(file_path, mode="r+b") as fp:
            fp.seek(start)
            fp.write(res.content)
            
    

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(num_of_thread) as executor:
        for i in range(num_of_thread):
            start = num_of_thread * i
            if i == num_of_thread - 1:
                end = file_size
            else:
                end = start + chunk_size

            executor.submit(
                handler,
                nico_url_data.session,
                start,
                end,
                content_link,
                file_path,
            )
    # threads = set()
    # for i in range(num_of_thread):
    #     start = num_of_thread * i
    #     if i == num_of_thread - 1:
    #         end = file_size
    #     else:
    #         end = start + chunk_size

    #     t = threading.Thread(
    #         target=handler,
    #         kwargs={
    #             "start": start,
    #             "end": end,
    #             "video_url": content_link,
    #             "file_path": file_path,
    #             "session": nico_url_data.session,
    #         },
    #     )
    #     # t.setDaemon(True)
    #     threads.add(t)
    #     t.start()
    
    # while (t := threading.current_thread()) in threads:
    #     if t.isAlive():
    #         continue
        # thread.setDaemon(True)

    return title
