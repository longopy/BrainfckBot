import coloredlogs
import logging
import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler, InlineQueryHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from random import getrandbits
import bf2t

BOT_TOKEN = "BOT_TOKEN"
BOT_IMAGE = 'BOT_IMAGE'
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
    message = "Welcome to Brainf*ckBot. \n----------------------------------\nI hope you have fun.\n\nLook at the things you can do: \nℹ️ /help To display the full options\n🔒 /info To view the author"
    logger.debug('[/start] _id:{id} _username:{username}'.format(id=user.id, username=user.username))
    bot.send_message(chat_id=update.message.chat_id, text=message)


def help(bot, update):
    user = update.message.from_user
    message = "Brainf*ckBot. \n----------------------------------\nOptions:\nℹ️ /help To display the options\n🔒 /code <Natural language message> To code a message\n🔑 /decode <Brainfuck message> To decode a message\n🤓 /info To view the author\n\nNOW!\n You can use this bot on inline mode:\nSteps:\n1-Go to a friend's chat\n2-Type the command you want in the message box, naming the bot and adding a message\n(@Brainfckbot /code <text> or @Brainfckbot /decode <bf>)\n3-Send the result to your friends\nHAVE FUN!"
    logger.debug('[/help] _id:{id} _username:{username}'.format(id=user.id, username=user.username))
    bot.send_message(chat_id=update.message.chat_id, text=message)


def inline(bot, update):
    query = update.inline_query.query
    if not query:
        return
    query = query.split(" ", 1)
    text = query[1:]
    command = (query[0])[1:]
    result = message = ""
    if command == 'code':
        message = "Send coded text: "
        result = code(bot, update, text, True)
    if command == 'decode':
        message = "Send decoded text: "
        result = decode(bot, update, text, True)
    if result:
        results = list()
        text = InlineQueryResultArticle(
            id=hex(getrandbits(64))[2:],
            title="{message}".format(message=message),
            description="{text}".format(text=result),
            thumb_url=BOT_IMAGE,
            input_message_content=InputTextMessageContent(result))
        results.append(text)
        bot.answerInlineQuery(update.inline_query.id, results=results)


def code_command(bot, update, args):
    text = code(bot, update, args, False)
    bot.send_message(chat_id=update.message.chat_id, text=text)


def code(bot, update, input_text, inline_flag):
    if not input_text:
        bot.send_message(chat_id=update.message.chat_id, text="⚠️ You have not inserted any message to code")
    else:
        if inline_flag:
            user = update.inline_query.from_user
        else:
            user = update.message.from_user
        if len(input_text[0]) > 140:
            logger.warning('[/code] {inline} The maximum message size is 140 characters'.format(
                inline="[inline]" if inline_flag else ""))
            bot.send_message(chat_id=update.message.chat_id, text="⚠️ The maximum message size is 140 characters")
        else:
            text = ""
            for word in input_text:
                text = text + word + ' '
            bf_text = text_to_bf(text)
            logger.debug('[/code] {inline} _id:{id} _username:{username} _text:{text} _bf:{bf}'.format(
                inline="[inline]" if inline_flag else "", id=user.id, username=user.username,
                text=input_text[0], bf=bf_text))
            return bf_text


def decode_command(bot, update, args):
    text = decode(bot, update, args, False)
    bot.send_message(chat_id=update.message.chat_id, text=text)


def decode(bot, update, input_text, inline_flag):
    if not input_text:
        bot.send_message(chat_id=update.message.chat_id, text="⚠️ You have not inserted any message to decode")
    else:
        if inline_flag:
            user = update.inline_query.from_user
        else:
            user = update.message.from_user
        bf = ""
        for word in input_text:
            bf = bf + word + ' '
        text = bf_to_text(bf)
        logger.debug(
            '[/decode] {inline} _id:{id} _username:{username} _text:{text} _bf:{bf}'.format(
                inline="[inline]" if inline_flag else "", id=user.id, username=user.username,
                text=text, bf=bf))
        return text


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
        dispatcher.add_handler(CommandHandler('code', code_command, pass_args=True))
        dispatcher.add_handler(CommandHandler('decode', decode_command, pass_args=True))
        dispatcher.add_handler(CommandHandler('info', info))
        dispatcher.add_handler(InlineQueryHandler(inline))


    except Exception as ex:
        logger.exception("Failure to connect with the Telegram API")
        quit()

    finally:
        logger.info("Connection completed")

updater.start_polling()
logger.info("Listening...")
updater.idle()
