from django.core.management.base import BaseCommand
import logging

from datetime import datetime
from telegram.utils.request import Request
from telegram import (
	ReplyKeyboardMarkup, 
	ReplyKeyboardRemove, 
	InlineKeyboardButton, 
	KeyboardButton, 
	InlineKeyboardMarkup, 
	Update,
	Bot,
)
from telegram.ext import (
	Updater,
	CommandHandler,
	MessageHandler,
	Filters,
	ConversationHandler,
	CallbackContext,
	CallbackQueryHandler,
)

from django.conf import settings

from ugc.models import Profile
from ugc.models import Departments
from ugc.models import NeedTypes
from ugc.models import Requests

from ugc.buttons import BUTTON_JOIN
from ugc.buttons import BUTTON_HELP
from ugc.buttons import BUTTON_REQ
from ugc.buttons import BUTTON_REREQ
from ugc.buttons import BUTTON_SEND
from ugc.buttons import BUTTON_BACK
from ugc.buttons import BUTTON_CLOSE

from ugc.buttons import CARTON
from ugc.buttons import PAPER
from ugc.buttons import SETT

from ugc.buttons import FOOD
from ugc.buttons import COMMON
from ugc.buttons import TOOLS
from ugc.buttons import ADVANCE
from ugc.buttons import FORWAY

from ugc.buttons import get_base_reply_keyboard
from ugc.buttons import get_base_admin_keyboard
from ugc.buttons import get_req_reply_keyboard
from ugc.buttons import get_back_close_keyboard
from ugc.buttons import get_send_redo_keyboard

# Включим ведение журнала
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем константы этапов разговора
PRE_JOIN, JOIN, DEP, AMOUNT, NEEDTYPE, NEED, CONFIRM, ADMIN_LOG = range(8)
dep_v = amount_v = needType_v = need_v = ''
CONFIRM_V = False

new_reply_keyboard = [[KeyboardButton(BUTTON_REREQ)]]
new_markup = ReplyKeyboardMarkup(new_reply_keyboard, one_time_keyboard=False, resize_keyboard=True) 

# функция обратного вызова точки входа в разговор
def start(update, _):
	user = update.message.from_user
	chat_id = update.message.chat_id
	message_id = update.message.message_id
	print(message_id)
	try:
		admin = Profile.objects.get(name=user.username, status=Profile.ADMIN)
		if(admin):
			update.message.reply_text(
				text='Привет! '+user.username+' Поздравляю 🤝\n'
				'Админ панель теперь ваша 😅\n',
				reply_markup=get_base_admin_keyboard()
			)
			return ADMIN_LOG
		else:
			update.message.reply_text(
				text='⚠️ - Eсли вы не наш сотрудник\n'
				'Вы будете Заблокированы\n'
				'или можете быть Деактивированы\n'
				'Со стороны Администратора!\n'
				'Чтобы Начать нажмите на кнопку "'+BUTTON_JOIN+'"\n',
				reply_markup=get_base_reply_keyboard()
			)
			return PRE_JOIN
	except  Profile.DoesNotExist:
		print('user not fount')
		# todo

	update.message.reply_text(
		text='⚠️ - Eсли вы не наш сотрудник\n'
		'Вы будете Заблокированы\n'
		'или можете быть Деактивированы\n'
		'Со стороны Администратора!\n'
		'Чтобы Начать нажмите на кнопку "'+BUTTON_JOIN+'"\n',
		reply_markup=get_base_reply_keyboard()
	)
	return PRE_JOIN

def pre_join(update, _):
	update.message.reply_text(
		text='Вход Подтвержден ✅ \n\n'
		'Можете Нажать на кнопку "'+BUTTON_REQ+'"\n',
		reply_markup=get_req_reply_keyboard()	
	)

	print(logger)
	return JOIN

def join(update, _):
	user = update.message.from_user
	
	dep_reply_keyboard = [[SETT], [CARTON, PAPER]]
	dep_markup = ReplyKeyboardMarkup(dep_reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
	update.message.reply_text(
		text='Выберите Отдел \n\n'
		'Для какого Отдела плата?',
		reply_markup=dep_markup	
	)

	# переходим к этапу `DEP`
	return DEP

def department(update, _):
	user = update.message.from_user
	global dep_v
	dep_v = update.message.text

	cat_reply_keyboard = [[FOOD, COMMON], [TOOLS], [ADVANCE, FORWAY]]
	cat_markup = ReplyKeyboardMarkup(cat_reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
	update.message.reply_text(
		text='Выберие категорию нужды\n\n'
		'Если вы осложняетесь ответить тогда\n'
		'просто выберите пункт - ' + COMMON,
		reply_markup=cat_markup	
	)
	return NEEDTYPE

def needType(update, _):
	user = update.message.from_user
	global needType_v
	needType_v = update.message.text

	update.message.reply_text(
		text='Опишите за что нужно оплатить\n\n'
		'Пример:\n'
		'Обед на троих, 3та Лаваш \n'
		'3та БигМак, 9та Шашли \n'
		'6та 2хил салат, 2та 1.5 кола, 1та сок \n',
		reply_markup=ReplyKeyboardRemove()	
	)
	return NEED

def need(update, _):
	user = update.message.from_user
	global need_v
	need_v= update.message.text

	update.message.reply_text(
		text='Отправьте Обшую сумму\n\n'
		'⚠️ Используйте пробелы \n'
		'или знаки типа: `.` `,`\n'
		'Примеры:\n'
		'5 000 000 или\n'
		'5,000,000\n'
		'5.000.000\n',
	)
	return AMOUNT

def amount(update, _):
	user = update.message.from_user
	global amount_v
	amount_v= update.message.text
	update.message.reply_text(
		text='Все ли верно? \n\n'+
		'Отдел: - '+dep_v+'\n'+
		'Категория: - '+needType_v+'\n'+
		'Описание: - '+need_v+'\n'+
		'Сумма: '+amount_v+' so\'m\n'
		'Если все верно нажмите на кнопку'+BUTTON_SEND+'\n',
		reply_markup=get_send_redo_keyboard()
	)
	return CONFIRM

def req_update(update: Update, self) -> None:
	time = datetime.now().strftime("%Y-%m-%d %H:%M")
	"""Parses the CallbackQuery and updates the message text."""
	query = update.callback_query
	user = update.callback_query.from_user
	mID = query.message.message_id
	query.answer()

	r = Requests.objects.get(message_id=mID)
	
	if(int(query.data) == 1):
		status_icon = "✅"
		r.status = Requests.ACCEPTED
		r.save()
	elif(int(query.data) == 2):
		status_icon = "❌"
		r.status = Requests.REJECTED
		r.save()

	query.edit_message_text(
		text='Отправитель: @'+str(r.profile.name)+'\n'
		'Отдел: '+str(r.department)+'\nСумма: '+r.amount+'\n'
		'Статус: '+status_icon+' '+r.status+'\n'
		'Модератор Зароса: @'+user.username+'\n'
		'Время: '+time
	)
	reply_to = r.profile.external_id

	bot = Bot (
		token=settings.TOKEN,
		#base_url=settings.PROXY_URL,
	)
	m = bot.send_message(
		reply_to,
		text='Запрос ID: #'+str(r.reply_to_message_id)+'\n'
		'Статус: '+status_icon+' '+r.status+'\n'
		'Модератор Зароса: @'+user.username+'\n',
		reply_to_message_id = r.reply_to_message_id
	)

def req_send(update: Update, m_id):
	user = update.message.from_user
	global amount_v
	bot = Bot (
		token=settings.TOKEN,
		#base_url=settings.PROXY_URL,
	)
	keyboard = [
		[
			InlineKeyboardButton("✅ Подтвердить", callback_data='1'),
			InlineKeyboardButton("❌ Отвергнуть", callback_data='2'),
		],
	]

	reply_markup = InlineKeyboardMarkup(keyboard)

	m = bot.send_message(
		settings.REQ_SENT_TOKEN,
		text='Зопрос ! \n\n'+
		'Отпровитель: 👤 @'+user.username+'\n'+
		'Отдел: - '+dep_v+'\n'+
		'Категория: - '+needType_v+'\n'+
		'Описание: - '+need_v+'\n'+
		'Сумма: '+amount_v+' so\'m\n',
		reply_markup = reply_markup
	)

	r = Requests.objects.get(message_id=m_id)
	r.message_id = m.message_id
	r.save()

def confirm(update: Update, _):
	user = update.message.from_user
	chat_id = update.message.chat_id
	message_id = update.message.message_id
	
	dep = Departments.objects.get(title=dep_v)
	needT = NeedTypes.objects.get(title=needType_v)
	p, _= Profile.objects.get_or_create(
		external_id = chat_id,
		defaults ={
			'name': user.username,
			'department': Departments.objects.get(id = dep.id),
		}

	)
	r = Requests(
		profile=p,
		department=Departments.objects.get(id = dep.id),
		need_type=NeedTypes.objects.get(id = needT.id),
		need=need_v,
		amount=amount_v,
		message_id = message_id,
		reply_to = message_id,
	)
	r.save()
	
	update.message.reply_text(
		text='Отпрвлено ! \n'
		'От имени: 👤 '+user.username+'\n'
		'ID: #'+str(message_id)+' \n',
		reply_markup=new_markup
	)
	req_send(update,message_id)
	return ConversationHandler.END

# Обрабатываем команду /cancel если пользователь отменил разговор
def stop(update, _):
	# определяем пользователя
	user = update.message.from_user
	# Пишем в журнал о том, что пользователь не разговорчивый
	logger.info("Пользователь %s отменил разговор.", user.first_name)
	# Отвечаем на отказ поговорить
	update.message.reply_text(
		text='Запрос Отменен',
		reply_markup=new_markup
	)
	# Заканчиваем разговор.
	return ConversationHandler.END

# Определяем обработчик разговоров `ConversationHandler` 
# с состояниями GENDER, PHOTO, LOCATION и BIO
conv_handler = ConversationHandler( # здесь строится логика разговора
	# точка входа в разговор
	entry_points=[CommandHandler('start', start), MessageHandler(Filters.text(BUTTON_REREQ), pre_join)],
	# этапы разговора, каждый со своим списком обработчиков сообщений
	states={
		PRE_JOIN: [MessageHandler(Filters.text(BUTTON_JOIN), pre_join)],
		JOIN: [MessageHandler(Filters.text(BUTTON_REQ), join)],
		DEP: [MessageHandler(Filters.regex('^('+ CARTON +'|'+ PAPER +'|'+ SETT +')$'), department)],
		NEEDTYPE: [MessageHandler(Filters.regex('^('+FOOD+'|'+COMMON+'|'+TOOLS+'|'+ADVANCE+'|'+FORWAY+')$'), needType)],
		NEED: [MessageHandler(Filters.text, need)],
		AMOUNT: [MessageHandler(Filters.regex('\d[\,\.\ ]{1}\d{1,2}'), amount)],
		CONFIRM: [MessageHandler(Filters.text(BUTTON_SEND), confirm), MessageHandler(Filters.text(BUTTON_CLOSE), stop)],
	},
	# точка выхода из разговора
	fallbacks=[CommandHandler('stop', stop)],
)

class Command(BaseCommand):
	help = 'telegram bot'

	def handle(self, *args, **options):
		# -- the connection
		request = Request (
			# connect_timeout=2.5,
			# read_timeout=1.0,
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
		updater.dispatcher.add_handler(CallbackQueryHandler(req_update))

		updater.start_polling()
		updater.idle()