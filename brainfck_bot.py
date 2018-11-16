import coloredlogs
import logging
import telegram
from telegram.ext import Updater, CommandHandler

import bf2t

BOT_TOKEN = "BOT_TOKEN"
BOT = telegram.Bot(token=BOT_TOKEN)
updater = Updater(BOT_TOKEN)

logger = logging.getLogger('BrainfckBot')
coloredlogs.install(level='DEBUG', logger=logger, milliseconds=True)


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
        new_bin = [abs(ord(char) - b)
                   for b in bins].index(min([abs(ord(char) - b)
                                             for b in bins]))
        appending_character = ""
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


def bf_to_text(string):
    parser = bf2t.BFInterpreter()
    return parser.execute(string)


def start(bot, update):
    user = update.message.from_user
    message = "Welcome to Brainf*ckBot. \n----------------------------------\nOptions:\nℹ️ /help To display the options\n🔒 /code <Natural language message> To code a message\n🔑 /decode <Brainfuck message> To decode a message\n🤓 /info To view the author"
    logger.debug('[/start] _id:{id} _username:{username}'.format(id=user.id, username=user.username))
    bot.send_message(chat_id=update.message.chat_id, text=message)


def help(bot, update):
    user = update.message.from_user
    message = "Brainf*ckBot. \n----------------------------------\nOptions:\nℹ️ /help To display the options\n🔒 /code <Natural language message> To code a message\n🔑 /decode <Brainfuck message> To decode a message\n🤓 /info To view the creator"
    logger.debug('[/help] _id:{id} _username:{username}'.format(id=user.id, username=user.username))
    bot.send_message(chat_id=update.message.chat_id, text=message)


def code(bot, update, args):
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text="⚠️ You have not inserted any message to code")
    else:
        user = update.message.from_user
        if len(args[0]) > 140:
            logger.warning('[/code] The maximum message size is 140 characters')
            bot.send_message(chat_id=update.message.chat_id, text="⚠️ The maximum message size is 140 characters")
        else:
            text = ""
            for word in args:
                text = text + word + ' '
            bf_text = text_to_bf(text)
            logger.debug('[/code] _id:{id} _username:{username} _text:{text}'.format(id=user.id, username=user.username,
                                                                                     text=text))
            bot.send_message(chat_id=update.message.chat_id, text=bf_text)


def decode(bot, update, args):
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text="⚠️ You have not inserted any message to decode")
    else:
        user = update.message.from_user
        if len(args[0]) > 140:
            logger.warning('[/decode] The maximum message size is 140 characters')
            bot.send_message(chat_id=update.message.chat_id, text="⚠️ The maximum message size is 140 characters")
        else:
            bf = ""
            for word in args:
                bf = bf + word + ' '
            text = bf_to_text(bf)
            logger.debug('[/decode] _id:{id} _username:{username} _bf_text:{text}'.format(id=user.id, username=user.username, text=bf))
            bot.send_message(chat_id=update.message.chat_id, text=text)


def info(bot, update):
    user = update.message.from_user
    message = "Bot created by 👨‍💻 @iLongo (ilongo.github.io) \nThanks to bareba and yiangos"
    logger.debug('[/info] _id:{id} _username:{username}'.format(id=user.id, username=user.username))
    bot.send_message(chat_id=update.message.chat_id, text=message)


if __name__ == "__main__":
    logger.info("Starting...")

    try:
        logger.info("Connecting to the Telegram API...")
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('help', help))
        dispatcher.add_handler(CommandHandler('code', code, pass_args=True))
        dispatcher.add_handler(CommandHandler('decode', decode, pass_args=True))
        dispatcher.add_handler(CommandHandler('info', info))

    except Exception as ex:
        logger.exception("Failure to connect with the Telegram API")
        quit()

    finally:
        logger.info("Connection completed")

updater.start_polling()
logger.info("Listening...")
updater.idle()
