import telebot
import logging
from telebot import types
from telebot.types import InputMediaPhoto
import sqlite3
import threading
import time
import traceback
from random import randint
import string
import random

admins = ['1841710225', '408820423', '151732063']

#token = ''
token = ''

bot = telebot.TeleBot(token)

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

'''

РЕГА

'''

def db_table_val_reg(user_id: int, username: str, uid: str):
	cursor.execute('INSERT INTO users (user_id, username, uid) VALUES (?, ?, ?)', (user_id, username, uid))
	conn.commit()

def db_table_upd_username(user_id: int, username: str):
	cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
	conn.commit()



@bot.message_handler(commands=["start"])
def start(m, res=False):
	if m.chat.type == 'private':

		cursor.execute("SELECT * FROM users")
		records = cursor.fetchall()

		all_mbrs = []

		for ch in records:
			all_mbrs.append(ch[1])

		if m.chat.id not in all_mbrs:
			#uid = randint(100000000, 999999999)
			length = 10
			letters_and_digits = string.ascii_letters + string.digits
			uid = ''.join(random.sample(letters_and_digits, length))

			print(str(m.chat.id) + f'(@{m.from_user.username}) зарегестрировался. Его uid: {uid}')
			db_table_val_reg(user_id=m.chat.id, username=f'{str(m.from_user.username)}', uid=uid)
			bot.send_message(m.chat.id, f'You have successfully registered! Your UID: {uid}')
			for admid in admins:
				try:
					bot.send_message(admid, str(m.chat.id) + f'(@{m.from_user.username}) зарегестрировался. Его uid: {uid}')
				except:
					pass
		else:

			cursor.execute("SELECT * FROM users")
			records = cursor.fetchall()

			for i in records:

				if i[1] == m.chat.id:
					if m.from_user.username != i[2]:
						db_table_upd_username(m.chat.id, m.from_user.username)
					bot.send_message(m.chat.id, f'Your UID: {i[3]}')
					break






@bot.message_handler(content_types=["text"])
def handle_text(message):
	if message.chat.type == 'private':

		if message.text == '/admin':
			if str(message.chat.id) in admins:
				try:
					bot.send_message(message.chat.id, 'Admin Menu.\n\nAvailable commands:\n/listusers - all registered users, them data\n/user [userid] - data of specific user')
				except:
					bot.send_message(message.chat.id, str(traceback.format_exc()))

		if message.text == '/listusers':
			if str(message.chat.id) in admins:

				try:
					cursor.execute("SELECT * FROM users ORDER BY uid DESC")
					records = cursor.fetchall()
					us = ''
					t = 0
					for d in records:
						us = us + str(d[1]) + ' - ' + str(d[2]) + ' - ' + str(d[3]) + '\n'
						t = t+1


					f = open('t.txt', 'w')
					f.write(f'total users: {len(records)}\n\ndata\nTG_ID - Ref.Link - Ref.Amount:\n\n{us}')
					f.close()
					bot.send_document(message.chat.id, open('t.txt', 'rb'))
					#bot.send_message(message.chat.id, f'total users: {len(records)}\n\ndata\nTG_ID - Ref.Link - Ref.Amount:\n\n{us}')
				except:
					bot.send_message(message.chat.id, str(traceback.format_exc()))


		if '/user' in message.text:
			if str(message.chat.id) in admins:
				try:
					cursor.execute("SELECT * FROM users")
					records = cursor.fetchall()
					targetus = message.text.split('/user ')[1]

					for g in records:
						if str(g[1]) == str(targetus):
							h = 1
							bot.send_message(message.chat.id, 'data\nTG_ID - Ref.Link - Ref.Amount:')
							bot.send_message(message.chat.id, str(g[1]) + ' - ' + str(g[2]) + ' - ' + str(g[3]))
							break
						else:
							h = 0
							pass
					if h == 0:
						bot.send_message(message.chat.id, 'user with this id was not found')

				except:
					bot.send_message(message.chat.id, str(traceback.format_exc()))

		if message.text == '/send' and str(message.chat.id) in admins:
			bot.reply_to(message, 'Отправьте сообщение для рассылки (картинки не поддерживаются)')
			bot.register_next_step_handler(message, sender)



def sender(message):
    cursor.execute("SELECT * FROM users")
    records = cursor.fetchall()
    for ch in records:
        try:
            time.sleep(1)
            bot.send_message(ch[1], message.text)
        except:
            pass
    bot.reply_to(message, 'Рассылка завершена.')


while True:
	try:
		bot.polling(none_stop=True, interval=0)
	except:
		for ad in admins:
			try:
				bot.send_message(ad, str(traceback.format_exc()))
			except:
				pass
