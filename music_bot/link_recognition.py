import re
from enum import Enum

# detect platform
# check if it's a playlist or not
# return platform 

YTB_URL = re.compile(
    r"((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)
BIL_URL = re.compile(
    r"((?:https?:)?\/\/)?((?:www)\.)?((?:bilibili\.com|b23.tv))(\/video)?\/((?:[\w\-]+))(\/?\?)?(\S+)?$"
)
BIL_ID = re.compile(r"(av[0-9]{6,}|BV[a-zA-Z]{6,})")
SCL_URL = re.compile(r"(https?:\/\/)?(www.)?(m\.)?soundcloud\.com\/[\w\-\.]+(\/)+[\w\-\.]+/?$")
NIC_URL = re.compile(r"^((?:https?:)?\/\/)?((?:www|sp)\.)?((?:nicovideo\.jp))\/?(watch|user\/\d+)?\/?(sm\d+|mylist\/\d+)?")
NIC_ID = re.compile(r"(sm[0-9]{6,})")

class Platform(Enum):
    Ytb = "Youtube"
    Bil = "Bilibili"
    Scl = "SoundCloud"
    Nic = "NicoNico"
    Unknown = "Unknown"