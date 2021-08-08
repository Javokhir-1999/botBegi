from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.utils.request import Request

from ugc.models import Message
from ugc.models import Profile
from ugc.models import Departments

import datetime
from logging import getLogger
from subprocess import Popen
from subprocess import PIPE

from ugc.config import load_config
from ugc.buttons import BUTTON_JION
from ugc.buttons import BUTTON_HELP
from ugc.buttons import get_base_reply_keyboard

# main keyboard
reply_keyboard = [['/join', '/help']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

def close_keyboard(update):
	update.message.reply_text('Ok', reply_markup=ReplyKeyboardRemove())

# log_errors
def log_errors(f):
	def inner(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:
			error_message = f'an Error occured: {e}'
			print(error_message)
			raise e

	return inner

# functions for command hendle
@log_errors
def do_echo(update: Update, context: CallbackContext):
	chat_id = update.message.chat_id
	text = update.message.text

	p, _= Profile.objects.get_or_create(
		external_id = chat_id,
		department = Departments.objects.get(id = 1),
		defaults ={
			'name': update.message.from_user.username,
		}

	)
	m = Message(
		profile=p,
		text=text,
	)
	m.save()

	reply_text = f'Your ID = {chat_id}\nMessage ID: {m.pk}\n{text}'
	update.message.reply_text(
		text=reply_text
	)

@log_errors
def do_start(update: Update, context: CallbackContext):
	update.message.reply_text(
		text='Привет! Этот бот принадлежит для\n'
		'персонала Компании ООО Демо и если вы \n'
		'не наш сотрудник, вы будете заблокированы\n'
		'А Если Да тогда Выберите команду /join \n'
		'и следуйте дольнейшим укозаниям\n',
		reply_markup=markup
	)

@log_errors
def do_join(update: Update, context: CallbackContext):

	#close_keyboard(update)
	# update.message.reply_text(
	# 	text='Выберите отдел: \n\n'
	# 	'Брусчатка цех\n'
	# 	'Бумажный цех\n'
	# 	'Картонка цех\n',
	# )
	
	# main keyboard
	reply_keyboard = [['/request', '/help']]
	request_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

	update.message.reply_text(
		text='Вход Подтвержден ! \n\n'
		'Подтверждение требуется тоько один раз\n'
		'Теперь вы можете осуществлять Запросы\n',
		reply_markup=request_markup	
	)



@log_errors
def do_count(update: Update, context: CallbackContext):
	chat_id=update.message.chat_id

	p, _= Profile.objects.get_or_create(
		external_id = chat_id,
		defaults ={
			'name': update.message.from_user.username,
		}
	)
	count = Message.objects.filter(profile=p).count()
	
	update.message.reply_text(
		text=f'you have {count} messages',
	)


class Command(BaseCommand):
	help = 'telegram bot'

	def handle(self, *args, **options):
		# -- the connection
		request = Request (
			connect_timeout=0.5,
			read_timeout=1.0,
		)
		bot = Bot (
			request=request,
			token=settings.TOKEN,
			#base_url=settings.PROXY_URL,
		)	
		print(bot.get_me())

		# -- process hendlers
		updater = Updater(
			bot=bot,
			use_context=True,
		)

		start_hendler = CommandHandler('start', do_start)
		count_hendler = CommandHandler('count', do_count)
		join_hendler = CommandHandler('join', do_join)
		
		#message_hendler = MessageHandler(Filters.text, do_echo)
		
		updater.dispatcher.add_handler(start_hendler)
		updater.dispatcher.add_handler(count_hendler)
		updater.dispatcher.add_handler(join_hendler)
		#updater.dispatcher.add_handler(message_hendler)


		# launching of infinite in going data
		updater.start_polling()
		updater.idle()