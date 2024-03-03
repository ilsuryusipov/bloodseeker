#!/usr/bin/env python3
import telebot
from telebot import apihelper
from telebot import types
from send import get_video_title, get_video_info_by_keyword
import re
from multiprocessing import Process
import json

token = ""
proxy = {'https':'socks5h://127.0.0.1:9150'}
save_file_name = "SongsList.txt"
bot = telebot.TeleBot(token)
apihelper.proxy = proxy
YOUTUBE_URL = 'https://www.youtube.com/watch?v='
 
def generate_inline_keyboard(buttons_list: list, type_of_keyboard = None):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 2
    for button_info in buttons_list:
        if type_of_keyboard == 'youtube':
            video_id = button_info['id']
            button = types.InlineKeyboardButton(text = str(button_info['title']).replace("&quot;", '"'), callback_data = f'youtube {video_id}')
        else:
            button = types.InlineKeyboardButton(text = button_info['title'], callback_data = button_info['id'])
        keyboard.add(button)
 
    return keyboard
    
    
def get_pagination(page, text, current_page):
    button_action = ''
    callback_data_json = {
        "button_action": button_action,
        "prev_page_token": page.prev_page_token,
        "next_page_token": page.next_page_token
        }
 
    keyboard_pag = generate_inline_keyboard(page.videos_list, type_of_keyboard= 'youtube')
 
    if not page.next_page_token and not page.prev_page_token:
        pass
    elif not page.prev_page_token:
        callback_data_json['button_action'] = 'next_page'
        callback_data_json['page_token'] = page.next_page_token
        calback_data_str = json.dumps(callback_data_json)
        next_page_button = telebot.types.InlineKeyboardButton('>>>', callback_data = f'next_page {text} {page.next_page_token}')
        #next_page = telebot.types.InlineKeyboardButton(f'>>>', callback_data = calback_data_str)
        current_page_button = telebot.types.InlineKeyboardButton(f'страница {current_page}', callback_data= f"{current_page}")
        keyboard_pag.row(current_page_button, next_page_button)
    elif not page.next_page_token:
        prev_page_button = telebot.types.InlineKeyboardButton('<<<', callback_data = f'prev_page {text} {page.prev_page_token}')
        current_page_button = telebot.types.InlineKeyboardButton(f'страница {current_page}', callback_data= f"{current_page}")
        keyboard_pag.row(prev_page_button, current_page)
    elif page.next_page_token and page.prev_page_token:
        prev_page_button = telebot.types.InlineKeyboardButton('<<<', callback_data = f'prev_page {text} {page.prev_page_token}')
        next_page_button = telebot.types.InlineKeyboardButton('>>>', callback_data = f'next_page {text} {page.next_page_token}')
        current_page_button = telebot.types.InlineKeyboardButton(f'страница {current_page}', callback_data= f"{current_page}")
        keyboard_pag.row(prev_page_button, current_page, next_page_button)
    else: 
        raise ValueError("not correct page")
 
    return keyboard_pag
 
 
def generate_standart_keyboard():
    keyboard  = generate_inline_keyboard([
        {'title' : "Плейлист", 'id' : "playlist"}, 
        {'title' : "Что играет?", 'id' : "current_song"}
        ])
    return keyboard
 
 
def in_process(chat_id, message_id = None, keyboard = None):
    if message_id:
        message = bot.edit_message_text("Идет загрузка...", chat_id, message_id, reply_markup = keyboard)
    else:
        message = bot.send_message(chat_id, "Идет загрузка...")
    return message.message_id
 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет, а может быть и ну", reply_markup=generate_standart_keyboard())
 
@bot.callback_query_handler(func=lambda call: True)
def ans(call):
        youtube_url = 'https://www.youtube.com/watch?v='
        message = call.message
        print(call.data)
 
        if call.data == 'playlist':
            message_id = in_process(message.chat.id)
            bot.edit_message_text(get_song_list(), message.chat.id, message_id, disable_web_page_preview= True, reply_markup = generate_standart_keyboard())
        if call.data == 'current_song':
            message_id = in_process(message.chat.id)
            bot.edit_message_text(get_current_song(), message.chat.id, message_id, reply_markup = generate_standart_keyboard())
        if re.match(r'youtube', call.data):
            message_id = in_process(message.chat.id)
            video_id = call.data.split(" ")[1]
            bot.edit_message_text(f'Видео добавлено в плейлист {youtube_url+video_id}', message.chat.id, message_id, reply_markup = generate_standart_keyboard())
 
        if re.match(r'prev_page', call.data):
            in_process(message.chat.id, message.message_id, message.reply_markup)
 
            current_page = str(message.text).split()[-1]
            prev_page = int(current_page) - 1
 
            page_token = str(call.data).split(" ")[-1]
            callback_data = str(call.data).split(" ")[0]
 
            keyword = str(call.data).replace(page_token, "").replace(callback_data, "").strip()
            page = get_video_info_by_keyword(keyword, page_token)
            keyboard_pag = get_pagination(page, keyword)
 
            bot.edit_message_text( f'вот что нашлось на запрос: страница {prev_page}', message.chat.id, message.message_id, reply_markup = keyboard_pag)
 
        if re.match(r'next_page', call.data):
            in_process(message.chat.id, message.message_id, message.reply_markup)
            current_page = str(message.text).split()[-1]
            next_page = int(current_page) + 1
 
            page_token = str(call.data).split(" ")[-1]
            callback_data = str(call.data).split(" ")[0]
 
            keyword = str(call.data).replace(page_token, "").replace(callback_data, "").strip()
            page = get_video_info_by_keyword(keyword, page_token)
            keyboard_pag = get_pagination(page, keyword)
            bot.edit_message_text( f'вот что нашлось на запрос: страница {next_page}', message.chat.id, message.message_id, reply_markup=keyboard_pag)
 
@bot.message_handler()
def send_answer(message):
    current_page = 1
    message_text = message.text
    message_id = in_process(message.chat.id)
    page = get_video_info_by_keyword(message_text)
    keyboard_pag = get_pagination(page, message_text, current_page)
    #bot.send_message(message.chat.id, f'Вот что нашлось на этот запрос:   страница {current_page}', reply_markup = keyboard_pag)
    bot.edit_message_text(
        f'Вот что нашлось на этот запрос:', 
        message.chat.id, 
        message_id, 
        reply_markup = keyboard_pag)
 
 
def get_song_list():
    song_list = []
    with open(save_file_name, 'r') as file:
        for line in file:
            song_list.append(str(line).strip())
    return  get_video_title(song_list)
 
def get_current_song():
    with open(save_file_name, 'r') as file:
        first_line = file.readline()
    return first_line
 
def listener(messages):
    for m in messages:
        print(str(m.text), str(m.chat.username))
 
def main():
    bot.set_update_listener(listener)
    bot.polling(none_stop=True)
 
    
if __name__ == "__main__":
    main()
