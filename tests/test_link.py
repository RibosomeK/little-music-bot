from music_bot.link_recognition import YTB_URL, BIL_URL
import re


TEST_YTB_LINKS = (
    "https://m.youtube.com/watch?v=DFYRQ_zQ-gk",
    "http://m.youtube.com/watch?v=DFYRQ_zQ-gk",
    "https://www.youtube.com/v/DFYRQ_zQ-gk?fs=1&hl=en_US",
    
    "https://m.youtube.com/embed/DFYRQ_zQ-gk?autoplay=1",
    "http://m.youtube.com/embed/DFYRQ_zQ-gk?autoplay=1",
    "https://www.youtube.com/embed/DFYRQ_zQ-gk?autoplay=1",
    
    "https://youtu.be/DFYRQ_zQ-gk?t=120",
    "https://youtu.be/DFYRQ_zQ-gk",
    "http://youtu.be/DFYRQ_zQ-gk"
)


TEST_BIL_LINKS = (
    "https://www.bilibili.com/video/BV1v54y1u7z2",
    "http://www.bilibili.com/video/BV1v54y1u7z2",
    "https://www.bilibili.com/video/av865444322",
    "http://www.bilibili.com/video/av865444322",
    "https://www.bilibili.com/video/BV1v54y1u7z2/?share_source=copy_web",
    "http://www.bilibili.com/video/BV1v54y1u7z2/?share_source=copy_web",
    "https://www.bilibili.com/video/BV1v54y1u7z2/?spm_id_from=333.1008",
    "http://www.bilibili.com/video/BV1v54y1u7z2/?spm_id_from=333.1008"
    
    "https://m.bilibili.com/video/BV1v54y1u7z2",
    "http://m.bilibili.com/video/BV1v54y1u7z2",
    "https://m.bilibili.com/video/av865444322",
    "http://m.bilibili.com/video/av865444322",
    "https://m.bilibili.com/video/BV1v54y1u7z2/?share_source=copy_web",
    "http://m.bilibili.com/video/BV1v54y1u7z2/?share_source=copy_web",
    "https://m.bilibili.com/video/BV1v54y1u7z2/?spm_id_from=333.1008",
    "http://m.bilibili.com/video/BV1v54y1u7z2/?spm_id_from=333.1008"
)


def test_ytb():
    for link in TEST_YTB_LINKS:
        assert re.search(YTB_URL, link) != None
        

def test_bil():
    for link in TEST_BIL_LINKS:
        assert re.search(BIL_URL, link) != None