
# Simple Music Bot Powered by Telegram Bot

This is a simple bot that can download music from video website, for some songs or podcasts aren't release on Spotify or other platforms. Now it only supports Youtube and Bilibili, and not supports playlists or batch download.

## Known Bugs:
1. The download speed would be extremely limited of video duration longer than 10mins
2. if sending a playlist link, only the first audio would be downloaded.
2. special chars in the title would be discard like `【` , `】`. It might be caused by Python itself (see issues: [missing punctuations](https://github.com/python-telegram-bot/python-telegram-bot/issues/3405) )

## Requirements:

- Python version >= 3.8
- a Telegram bot token
- ffmepg
- (recommend) Linux system

## Usage:

1. install needed libraries.

   ```bash
   pip install -r requirments.txt
   ```

2. start the bot.

   ```bash
   python main.py YOUR-BOT-TOKEN
   ```

## Credit

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [youtube-dl](https://github.com/ytdl-org/youtube-dl)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
- [ffmpeg](https://github.com/FFmpeg/FFmpeg)

## Roadmap

1. fixed speed limitation
2. better error catching
3. add playlist support
4. add more platform support
5. ...
