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
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
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
from ugc.buttons import BUTTON_JOIN
from ugc.buttons import BUTTON_HELP
from ugc.buttons import BUTTON_REQ
from ugc.buttons import BUTTON_SEND
from ugc.buttons import BUTTON_BACK
from ugc.buttons import BUTTON_CLOSE
from ugc.buttons import COMMON
from ugc.buttons import CARTON
from ugc.buttons import PAPER
from ugc.buttons import SETT
from ugc.buttons import get_base_reply_keyboard
from ugc.buttons import get_req_reply_keyboard
from ugc.buttons import get_back_close_keyboard
from ugc.buttons import get_send_back_close_keyboard
import re

back_keyboard = [[BUTTON_BACK]]
back_markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=False, resize_keyboard=True)
AMOUNT = DEP = NEED =''
CONFIRM = False

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

@log_errors
def do_start(update: Update, context: CallbackContext):
	update.message.reply_text(
		text='Привет! Этот бот принадлежит для\n'
		'персонала Компании ООО Демо и если вы \n'
		'не наш сотрудник, вы будете заблокированы\n'
		'А Если наш, нажмите на кнопку "'+BUTTON_JOIN+'"\n',
		reply_markup=get_base_reply_keyboard()
	)
	return 0

@log_errors
def do_join(update: Update, context: CallbackContext):
	join_answer = update.message.text
	if join_answer == BUTTON_JOIN:
		update.message.reply_text(
			text='Вход Подтвержден ! \n\n'
			'Подтверждение требуется тоько один раз\n'
			'Теперь вы можете осуществлять Запросы\n'
			'Нажмите на кнопку "'+BUTTON_REQ+'"\n'
			'или отправить любое сообщение',
			reply_markup=get_req_reply_keyboard()	
		)
	elif join_answer == BUTTON_REQ:
		update.message.reply_text(text=join_answer+'req')
		return 1
	elif join_answer == BUTTON_HELP:
		update.message.reply_text(text=join_answer+'-h')
		return 5
	elif join_answer == BUTTON_CLOSE:
		update.message.reply_text(text='Отменена !')
		return ConversationHandler.END		
	if join_answer == BUTTON_REQ:
		return 1 

@log_errors
def do_req(update: Update, context: CallbackContext, user_data):
	req_answer = update.message.text
	update.message.reply_text(text=req_answer+'req')
	if req_answer == BUTTON_REQ:
		dep_reply_keyboard = [[COMMON, CARTON], [PAPER, SETT],[BUTTON_CLOSE]]
		dep_markup = ReplyKeyboardMarkup(dep_reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
		update.message.reply_text(
			text='Выберите Отдел \n\n'
			'Для какого Отдела плата?',
			reply_markup=dep_markup	
		)
	elif req_answer == COMMON or req_answer == CARTON or req_answer == PAPER or req_answer == SETT:
		DEP = req_answer
		return 2
	elif join_answer == BUTTON_CLOSE:
		req_answer.message.reply_text(text='Отменена !')
		return ConversationHandler.END

@log_errors
def get_need(update: Update, context: CallbackContext, user_data):
	need_answer = update.message.text
	if need_answer == COMMON or need_answer == CARTON or need_answer == PAPER or need_answer == SETT:
		update.message.reply_text(
			text='Опишите за что нужно оплатить\n\n'
			'Пример:\n'
			'Плата За Еду\n'
			'Описание: Обед на троих \n'
			'3та Лаваш \n'
			'3та БигМак \n'
			'9та Шашли \n'
			'6та 2хил салат \n'
			'2та 1.5 кола, 1та сок \n',
			reply_markup=get_back_close_keyboard()	
		)
		
	elif need_answer == BUTTON_BACK:
		return 1
	elif need_answer == BUTTON_CLOSE:
		req_answer.message.reply_text(text='Отменена !')
		return ConversationHandler.END
	else:
		NEED = need_answer
		return 3

@log_errors
def get_amount(update: Update, context: CallbackContext,user_data):
	amount = update.message.text
	if NEED:
		update.message.reply_text(
			text='Отправьте Обшую сумму только в числах \n\n'
			'Примеры:\n'
			'5.000.000\n'
			'5000000\n'
		)
	elif amount == BUTTON_BACK:
		return 2
	elif amount == BUTTON_CLOSE:
		req_answer.message.reply_text(text='Отменена !')
		return ConversationHandler.END
	else:
		amount = update.message.text
		if not re.search("^[a-zA-Z]", amount):
			AMOUNT = amount
			return 4
@log_errors
def get_confirm(update: Update, context: CallbackContext):
	conrirm = update.message.text
	if conrirm == BUTTON_SEND:
		update.message.reply_text(
			text='Отлично Все Сделано\n',
			reply_markup=get_req_reply_keyboard(),
		)
		CONFIRM = True
		return ConversationHandler.END
	elif conrirm == BUTTON_BACK:
		return 3
	elif conrirm == BUTTON_CLOSE:
		req_answer.message.reply_text(text='Отменена !')
		return ConversationHandler.END
	else:
		update.message.reply_text(
			text='Все ли верно? \n\n'+NEED+'\n'+AMOUNT+'n'
			'Если все верно нажмите на кнопку'+BUTTON_SEND+'\n',
			reply_markup=get_send_back_close_keyboard()
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

@log_errors
def do_help(update: Update, context: CallbackContext):
	update.message.reply_text(
		text='Покачто нет данных ! \n\n'
		'Обратись в администрацию\n',
		reply_markup=get_base_reply_keyboard()	
	)

@log_errors
def do_stop(bot, update):
	update.message.reply_text("Стоп!")
	return ConversationHandler.END

conv_handler = ConversationHandler(
		# Точка входа в диалог.
		# В данном случае — команда /start. Она задаёт первый вопрос.
		entry_points=[CommandHandler('start', do_start)],
		
		# Словарь состояний внутри диалога. 
		# Наш вариант с двумя обработчиками,
		# фильтрующими текстовые сообщения.
		states={
		# Функция читает ответ на второй вопрос и завершает диалог.
		0: [MessageHandler(Filters.text, do_join, pass_user_data=True)],
		1: [MessageHandler(Filters.text, do_req, pass_user_data=True)],
		2: [MessageHandler(Filters.text, get_need, pass_user_data=True)],
		3: [MessageHandler(Filters.text, get_amount, pass_user_data=True)],
		4: [MessageHandler(Filters.text, get_confirm, pass_user_data=True)],
		5: [MessageHandler(Filters.text, do_help, pass_user_data=True)],
		},
		
		# Точка прерывания диалога. В данном случае — команда /stop.
		fallbacks=[CommandHandler('stop', do_stop)],
	)

class Command(BaseCommand):
	help = 'telegram bot'

	def handle(self, *args, **options):
		# -- the connection
		request = Request (
			connect_timeout=2.5,
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



		updater.dispatcher.add_handler(conv_handler)
		updater.dispatcher.add_handler(CommandHandler('start', do_join))
		updater.dispatcher.add_handler(CommandHandler('stop', do_stop))


		# start_hendler = CommandHandler('start', do_start)
		# join_hendler = MessageHandler(Filters.text(BUTTON_JOIN), do_join)
		# help_hendler = MessageHandler(Filters.text(BUTTON_HELP), do_help)
		# req_hendler = MessageHandler(Filters.text(BUTTON_REQ), do_req)
		
		# #message_hendler = MessageHandler(Filters.text, do_echo)
		# buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler)
		# updater.dispatcher.add_handler(start_hendler)
		# updater.dispatcher.add_handler(join_hendler)
		# updater.dispatcher.add_handler(help_hendler)
		# updater.dispatcher.add_handler(req_hendler)
		#updater.dispatcher.add_handler(message_hendler)


		# launching of infinite in going data
		updater.start_polling()
		updater.idle()