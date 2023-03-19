import os, logging

from telegram import Update
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
)

from .download import detect_url, download_audio


def start(update: Update, context: CallbackContext):
    if update.effective_chat is not None:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="猫猫在捏~ 可以发送 Youtube 或者 Bilibili 链接下载音频哦！"
        )


def echo(update: Update, context: CallbackContext):
    if update.effective_chat is not None:
        text = update.message.text
        id, platform = detect_url(text)
        if id and platform.value != "Unknown":
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"这是一个 {platform.value} 链接哦~ 猫猫收到了！",
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="猫猫试着帮你下载音频看看!"
            )
            try:
                file_name = download_audio(id, platform)
            except Exception as e:
                file_name = ""
                print(e)
            if os.path.exists(file_name):
                with open(file_name, mode="rb") as audio:
                    context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=audio,
                        filename=file_name,
                    )
                    print(f"{file_name=}")
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text="音频下好咯~ 请查收~"
                    )
                os.remove(file_name)
            else:
                print(f"file_name: {file_name}")
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text="呜呜呜，下载失败喵<(_ _)>"
                )

        else:
            text = update.message.text
            user_name = update.message.chat.full_name
            print(f"{user_name}: {text}")
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"这是什么？复读一下：{text}"
            )


def start_bot(token: str):

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()
