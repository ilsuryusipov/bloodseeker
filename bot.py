#!/usr/bin/env python3

import telebot
from telebot import apihelper
from telebot import types
import bot_config

token = bot_config.token
save_file_name = 'UrlsList.txt'
current_track_file = 'CurrentTrack.txt'
bot = telebot.TeleBot(token)

def generate_inline_keyboard(*answer):
	print('generate_inline_keyboard')
	print(f"answer: {answer}")
	keyboard = types.InlineKeyboardMarkup()
	temp_buttons = []
	for i in answer:
		temp_buttons.append(types.InlineKeyboardButton(text=i[0], callback_data=i[1]))
	keyboard.add(*temp_buttons)
	return keyboard

print('keyboard calculating')
keyboard = generate_inline_keyboard(['Playlist', 'playlist'], ['Current track?', 'current_track'] , ['What is next?', 'next_song'], ['Skip track', 'skip_track'])
print(keyboard)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	print('send_welcome')
	bot.send_message(message.chat.id, 'Hello, dude!')

@bot.message_handler(commands=['menu'])
def show_menu(message):
	print('show_menu')
	bot.send_message(message.chat.id, 'Enjoy our bot and try not to fuck yourself =)', reply_markup=keyboard)

@bot.message_handler(commands=['her'])
def send_her(message):
	print('send_her')
	bot.send_message(message.chat.id, '8=================3')

@bot.callback_query_handler(func=lambda call: True)
def ans(call):
	print('ans')
	message = call.message
	if call.data == 'playlist':
		#bot.send_message(message.chat.id, get_song_list(), disable_web_page_preview= True, disable_notification= True)
		bot.send_message(message.chat.id, get_song_list(), disable_web_page_preview=True, disable_notification=True)
	if call.data == 'current_track':
		bot.send_message(message.chat.id, get_current_track(), disable_notification=True)
	if call.data == 'next_song':
		bot.send_message(message.chat.id, get_next_song(), disable_notification=True)
	if call.data == 'skip_track':
		bot.send_message(message.chat.id, skip_track(), disable_notification=True)

def get_current_track():
	print('get_current_track')
	current_track = 'There is no current track!'
	try:
		with open(current_track_file, 'r') as file:
			current_track = file.readline()
	except:
		pass
	return current_track

def get_song_list():
	print('get_song_list')
	song_list = ''
	with open(save_file_name, 'r') as file:
		count = 1
		for line in file:
			if line:
				song_list += f'{count}. {line}'
				count += 1
	if song_list == '':
		return 'Empty playlist!'
	return 'Playlist:\n\n'+song_list

def get_next_song():
	print('get_next_song')
	next_track = ''
	with open(save_file_name, 'r') as file:
		next_track = file.readline()
		if next_track == '':
			next_track = 'There is no next track!'
	return next_track

def skip_track():
	print('skip_track')
	import os
	os.system('systemctl --user restart player.service')
	return 'Skipped!'

@bot.message_handler()
def handle_message(message):
	print('handle_message')
	print(f'MSG: {message.text}')

	if not message.entities:
		print('No Entities in message.')
		return

	message_has_url = False
	for entity in message.entities:
		if entity.type == 'url':
			offset = entity.offset
			length = entity.length
			url = message.text[offset:(offset+length)]
			message_has_url = True
		elif entity.type == 'text_link':
			url = entity.url
			message_has_url = True
		else:
			continue

		print(f'Queueing to file [{url}]')
		with open(save_file_name, 'a', encoding='utf-8') as my_file:
			my_file.write(f'{url}\n')

	if not message_has_url:
		print('Message has no URL')

def listener(message):
	for m in message:
		print(str(m))

def main():
	print('main')
	bot.set_update_listener(listener)
	bot.infinity_polling(True)
	print('after polling')

if __name__ == '__main__':
	main()
