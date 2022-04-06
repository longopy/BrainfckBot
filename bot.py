import logging
import os
import re
from random import getrandbits

from telegram import InlineQueryResultArticle, InputTextMessageContent, Bot, Update
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters, CallbackContext
from wrapt_timeout_decorator import timeout

import bf2t

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_IMAGE = os.environ.get("BOT_IMAGE")
MAX_LENGTH = os.environ.get("MAX_LENGTH", 350)
TIMEOUT = os.environ.get("TIMEOUT", 3)


def text_to_bf(data):
    glyphs = len(set([c for c in data]))
    number_of_bins = max(max([ord(c) for c in data]) // glyphs, 1)
    bins = [(i + 1) * number_of_bins for i in range(glyphs)]
    code = "+" * number_of_bins + "["
    code += "".join([">" + ("+" * (i + 1)) for i in range(1, glyphs)])
    code += "<" * (glyphs - 1) + "-]"
    code += "+" * number_of_bins
    current_bin = 0
    for char in data:
        new_bin = [abs(ord(char) - b) for b in bins].index(min([abs(ord(char) - b) for b in bins]))
        if new_bin - current_bin > 0:
            appending_character = ">"
        else:
            appending_character = "<"
        code += appending_character * abs(new_bin - current_bin)
        if ord(char) - bins[new_bin] > 0:
            appending_character = "+"
        else:
            appending_character = "-"
        code += (appending_character * abs(ord(char) - bins[new_bin])) + "."
        current_bin = new_bin
        bins[new_bin] = ord(char)
    return code


@timeout(TIMEOUT)
def bf_to_text(string):
    parser = bf2t.BFInterpreter()
    return parser.execute(string)


def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    message = "Welcome to Brainf*ckBot. \n----------------------------------\nI hope you have fun.\n\nLook at the things you can do: \nℹ️ /help To display the full options\n🔒 /info To view the author"
    logger.debug("[/start] _id:{id} _username:{username}".format(id=user.id, username=user.username))
    update.message.reply_text(text=message)


def help(update: Update, context: CallbackContext):
    user = update.message.from_user
    message = "Brainf*ckBot. \n----------------------------------\nOptions:\nℹ️ /help To display the options\n🤓 /info To view the author\n\nYou can send a natural language text or a brainfuck language text and the bot will translate it for you.\nTRY IT!\n\nNOW!\nYou can use this bot on inline mode:\nSteps:\n1-Go to a friend's chat\n2-Type the command you want in the message box, naming the bot and adding a message\n(@Brainfckbot <text> or <bf_text>)\n3-Send the result to your friends\nHAVE FUN!"
    logger.debug("[/help] _id:{id} _username:{username}".format(id=user.id, username=user.username))
    update.message.reply_text(text=message)


def inline(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return
    result = smart_command(update, query, True)
    message = "Send text:"
    if result:
        results = list()
        text = InlineQueryResultArticle(
            id=hex(getrandbits(64))[2:],
            title="{message}".format(message=message),
            description="{text}".format(text=result),
            thumb_url=BOT_IMAGE,
            input_message_content=InputTextMessageContent(result),
        )
        results.append(text)
        update.inline_query.answer(results=results)


def message_handler(update: Update, context: CallbackContext):
    text = update.message.text
    text = smart_command(update, text)
    if text:
        update.message.reply_text(text=text)


def smart_command(update: Update, input_text, inline_flag=False):
    input_is_text = set(input_text) - set(".,+-><[]")
    if input_is_text:
        command, result = code(input_text)
    else:
        command, result = decode(input_text)
    if inline_flag:
        username = update.inline_query.from_user.username
        user_id = update.inline_query.from_user.id
    else:
        username = update.message.from_user.username
        user_id = update.message.from_user.id
    if command == "code":
        text = input_text
        bf = result
        logger.info(
            f"[/{command}] {'[inline]' if inline_flag else ''} _:{user_id} _username:{username} _text:{text} _bf:{bf}"
        )
    elif command == "decode":
        text = result
        bf = input_text
        logger.info(
            f"[/{command}] {'[inline]' if inline_flag else ''} _id:{user_id} _username:{username} _bf:{text} _text:{bf}"
        )
    return result


def code(input_text):
    if len(" ".join(input_text)) > MAX_LENGTH:
        logger.warning(f"[/code] The maximum message size is {MAX_LENGTH} characters")
        text = f"⚠️ The maximum message size is {MAX_LENGTH} characters"
        return "code", text
    else:
        text = ""
        words = input_text.split(" ")
        for word in words:
            text = text + word + " "
        bf_text = text_to_bf(text)
        return "code", bf_text


def decode(input_text):
    bf = ""
    for word in input_text:
        bf = bf + word + " "
    try:
        text = bf_to_text(bf)
    except:
        text = "🖕Do you think I suck my thumb? Don't try to break me."
    return "decode", text


def info(update: Update, context: CallbackContext):
    user = update.message.from_user
    message = "Bot created by 👨‍💻 @longopy\nhttps://github.com/longopy\nThanks to bareba and yiangos"
    logger.debug("[/info] _id:{id} _username:{username}".format(id=user.id, username=user.username))
    update.message.reply_text(text=message)


if __name__ == "__main__":
    BOT = Bot(token=BOT_TOKEN)
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    logger = logging.getLogger("BrainfckBot")
    updater = Updater(BOT_TOKEN, use_context=True)
    logger.info("Starting...")
    try:
        logger.info("Connecting to the Telegram API...")
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help))
        dispatcher.add_handler(MessageHandler((Filters.text & (~Filters.regex('/info'))), message_handler))
        dispatcher.add_handler(CommandHandler("info", info))
        dispatcher.add_handler(InlineQueryHandler(inline))
    except Exception as ex:
        logger.exception("Failure to connect with the Telegram API")
        quit()
    finally:
        logger.info("Connection completed")
    updater.start_polling()
    logger.info("Listening...")
    updater.idle()
