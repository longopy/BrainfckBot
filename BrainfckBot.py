import telegram
from telegram.ext import Updater, CommandHandler
import bf2t

BOT_TOKEN = "BOT_TOKEN_HERE"
BOT = telegram.Bot(token=BOT_TOKEN)
updater = Updater(BOT.token)


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
    message = "Welcome to Brainf*ckBot. \n----------------------------------\nOptions:\nℹ️ /help To display the options\n🔒 /code <Message> To code a message\n🔑 /decode <Message to Decode> To decode a message\n🤓 /info To view the author"
    bot.send_message(chat_id=update.message.chat_id, text=message)


def help(bot, update):
    message = "Brainf*ckBot. \n----------------------------------\nOptions:\nℹ️ /help To display the options\n🔒 /code <Message> To code a message\n🔑 /decode <Message to Decode> To decode a message\n🤓 /info To view the creator"
    bot.send_message(chat_id=update.message.chat_id, text=message)


def code(bot, update, args):
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text="⚠️ You have not inserted any message to code")
    else:
        text = ""
        for word in args:
            text = text + word + ' '
        print(text_to_bf(text))
        bot.send_message(chat_id=update.message.chat_id, text=text_to_bf(text))


def decode(bot, update, args):
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text="⚠️ You have not inserted any message to decode")
    bf = ""
    for word in args:
        bf = bf + word + ' '
    bot.send_message(chat_id=update.message.chat_id, text=bf_to_text(bf))


def info(bot, update):
    message = "Bot created by 👨‍💻 @iLongo (ilongo.github.io) \nThanks to yiangos"
    bot.send_message(chat_id=update.message.chat_id, text=message)


dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

code_handler = CommandHandler('code', code, pass_args=True)
dispatcher.add_handler(code_handler)

decode_handler = CommandHandler('decode', decode, pass_args=True)
dispatcher.add_handler(decode_handler)

info_handler = CommandHandler('info', info)
dispatcher.add_handler(info_handler)

updater.start_polling()
updater.idle()
