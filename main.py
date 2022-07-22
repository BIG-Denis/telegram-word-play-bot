
import telebot
import json
from random import choice, randint
from collections import defaultdict


with open('token.json', 'r') as file:
    json_file = json.load(file)
    token = json_file['token']

bot = telebot.TeleBot(token=token)
used_words = defaultdict(list)
all_words = []
prevs = {}

with open('messages.json', 'r') as file:
    json_file = json.load(file)
    start_message = json_file["start_message"]
    win_message = json_file["win_message"]

with open('words.txt', 'r') as file:
    for word in file:
        if ' ' not in word:
            all_words.append(word.replace('\n', '').lower())


def enter_word(message, prev) -> int:
    if message.text.lower() in used_words[message.chat.id]:
        return 1
    if message.text.lower() not in all_words:
        return 2
    if prev[-1] in ('ь', 'ъ', 'ы'):
        if message.text.lower()[0] != prev[-2]:
            return 3
    elif message.text.lower()[0] != prev[-1]:
        return 3
    used_words[message.chat.id].append(message.text)
    return 0


def get_word(message, first: bool = False) -> str:
    global prevs
    letter = 'ъ'
    let_words = []
    while letter in ('ь', 'ъ', 'ы'):
        letter = message.text.lower()[-1] if not first else chr(randint(1072, 1103))
        if letter in ('ь', 'ъ', 'ы') and not first:
            letter = message.text.lower()[-2]
    for word in all_words:
        if word[0] == letter and word not in used_words[message.chat.id]:
            let_words.append(word)
    if len(let_words) == 0:
        bot.send_message(message.chat.id, win_message)
    ret_word = choice(let_words)
    prevs[message.chat.id] = ret_word
    return ret_word


@bot.message_handler(commands=['start', 'help'])
def start_menu(message):
    bot.send_message(message.chat.id, start_message)
    used_words[message.chat.id] = []


@bot.message_handler(commands=['words'])
def words_game_info(message):
    bot.send_message(message.chat.id, f'Ну что же, я начинаю, моё слово...')
    send_word = get_word(message, True)
    bot.send_message(message.chat.id, send_word)
    bot.register_next_step_handler_by_chat_id(message.chat.id, word_game)


def word_game(message):
    global used_words
    if message.text.lower() == 'хватит':
        bot.register_next_step_handler_by_chat_id(message.chat.id, start_menu)
        start_menu(message)
        return
    res = enter_word(message, prevs[message.chat.id])
    used_words[message.chat.id].append(message.text.lower())
    if res == 1:
        bot.send_message(message.chat.id, 'Это слово уже использовалось в игре! Давай другое!')
        bot.register_next_step_handler_by_chat_id(message.chat.id, word_game)
    if res == 2:
        bot.send_message(message.chat.id, 'Нет такого слова! Давай другое!')
        bot.register_next_step_handler_by_chat_id(message.chat.id, word_game)
    if res == 3:
        bot.send_message(message.chat.id, 'А букавки-то не совпадают! Давай другое!')
        bot.register_next_step_handler_by_chat_id(message.chat.id, word_game)
    if res == 0:
        send_word = get_word(message, False)
        bot.send_message(message.chat.id, send_word)
        bot.register_next_step_handler_by_chat_id(message.chat.id, word_game)


bot.infinity_polling()
