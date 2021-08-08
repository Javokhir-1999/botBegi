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
from ugc.buttons import BUTTON_REQ
from ugc.buttons import get_base_reply_keyboard
from ugc.buttons import get_req_reply_keyboard
from ugc.utils import logger_factory

# main keyboard
reply_keyboard = [['/join', '/help']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

config = load_config()

logger = getLogger(__name__)

debug_requests = logger_factory(logger=logger)


# `callback_data` -- это то, что будет присылать TG при нажатии на каждую кнопку.
# Поэтому каждый идентификатор должен быть уникальным
CALLBACK_BUTTON1_LEFT = "callback_button1_left"
CALLBACK_BUTTON2_RIGHT = "callback_button2_right"
CALLBACK_BUTTON3_MORE = "callback_button3_more"
CALLBACK_BUTTON4_BACK = "callback_button4_back"
CALLBACK_BUTTON5_TIME = "callback_button5_time"
CALLBACK_BUTTON6_PRICE = "callback_button6_price"
CALLBACK_BUTTON7_PRICE = "callback_button7_price"
CALLBACK_BUTTON8_PRICE = "callback_button8_price"
CALLBACK_BUTTON_HIDE_KEYBOARD = "callback_button9_hide"

CALLBACK_BUTTON_REQ = "callback_button_req"


TITLES = {
    CALLBACK_BUTTON1_LEFT: "Новое сообщение ⚡️",
    CALLBACK_BUTTON2_RIGHT: "Отредактировать ✏️",
    CALLBACK_BUTTON3_MORE: "Ещё ➡️",
    CALLBACK_BUTTON4_BACK: "Назад ⬅️",
    CALLBACK_BUTTON5_TIME: "Время ⏰",
    CALLBACK_BUTTON6_PRICE: "BTC 💰",
    CALLBACK_BUTTON7_PRICE: "LTC 💰",
    CALLBACK_BUTTON8_PRICE: "ETH 💰",
    CALLBACK_BUTTON_HIDE_KEYBOARD: "Спрять клавиатуру",

    CALLBACK_BUTTON_REQ: "Запросить ➡️",
}

# Глобально инициализируем клиент API Bittrex
#client = BittrexClient()


def get_base_inline_keyboard():
    """ Получить клавиатуру для сообщения
        Эта клавиатура будет видна под каждым сообщением, где её прикрепили
    """
    # Каждый список внутри `keyboard` -- это один горизонтальный ряд кнопок
    keyboard = [
        # Каждый элемент внутри списка -- это один вертикальный столбец.
        # Сколько кнопок -- столько столбцов
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON1_LEFT], callback_data=CALLBACK_BUTTON1_LEFT),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON2_RIGHT], callback_data=CALLBACK_BUTTON2_RIGHT),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON3_MORE], callback_data=CALLBACK_BUTTON3_MORE),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard2():
    """ Получить вторую страницу клавиатуры для сообщений
        Возможно получить только при нажатии кнопки на первой клавиатуре
    """
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON5_TIME], callback_data=CALLBACK_BUTTON5_TIME),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON6_PRICE], callback_data=CALLBACK_BUTTON6_PRICE),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON7_PRICE], callback_data=CALLBACK_BUTTON7_PRICE),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON8_PRICE], callback_data=CALLBACK_BUTTON8_PRICE),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4_BACK], callback_data=CALLBACK_BUTTON4_BACK),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


@debug_requests
def keyboard_callback_handler(update: Update, context: CallbackContext):
    """ Обработчик ВСЕХ кнопок со ВСЕХ клавиатур
    """
    query = update.callback_query
    data = query.data
    now = datetime.datetime.now()

    # Обратите внимание: используется `effective_message`
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == CALLBACK_BUTTON1_LEFT:
        # "Удалим" клавиатуру у прошлого сообщения
        # (на самом деле отредактируем его так, что текст останется тот же, а клавиатура пропадёт)
        query.edit_message_text(
            text=current_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        # Отправим новое сообщение при нажатии на кнопку
        context.bot.send_message(
            chat_id=chat_id,
            text="Новое сообщение\n\ncallback_query.data={}".format(data),
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON2_RIGHT:
        # Отредактируем текст сообщения, но оставим клавиатуру
        query.edit_message_text(
            text="Успешно отредактировано в {}".format(now),
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON3_MORE:
        # Показать следующий экран клавиатуры
        # (оставить тот же текст, но указать другой массив кнопок)
        query.edit_message_text(
            text=current_text,
            reply_markup=get_keyboard2(),
        )
    elif data == CALLBACK_BUTTON4_BACK:
        # Показать предыдущий экран клавиатуры
        # (оставить тот же текст, но указать другой массив кнопок)
        query.edit_message_text(
            text=current_text,
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON5_TIME:
        # Покажем новый текст и оставим ту же клавиатуру
        text = "*Точное время*\n\n{}".format(now)
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard2(),
        )
    # elif data in (CALLBACK_BUTTON6_PRICE, CALLBACK_BUTTON7_PRICE, CALLBACK_BUTTON8_PRICE):
    #     pair = {
    #         CALLBACK_BUTTON6_PRICE: "USD-BTC",
    #         CALLBACK_BUTTON7_PRICE: "USD-LTC",
    #         CALLBACK_BUTTON8_PRICE: "USD-ETH",
    #     }[data]

    #     try:
    #         current_price = client.get_last_price(pair=pair)
    #         text = "*Курс валюты:*\n\n*{}* = {}$".format(pair, current_price)
    #     except BittrexError:
    #         text = "Произошла ошибка :(\n\nПопробуйте ещё раз"
    #     query.edit_message_text(
    #         text=text,
    #         parse_mode=ParseMode.MARKDOWN,
    #         reply_markup=get_keyboard2(),
    #     )
    elif data == CALLBACK_BUTTON_HIDE_KEYBOARD:
        # Спрятать клавиатуру
        # Работает только при отправке нового сообщение
        # Можно было бы отредактировать, но тогда нужно точно знать что у сообщения не было кнопок
        context.bot.send_message(
            chat_id=chat_id,
            text="Спрятали клавиатуру\n\nНажмите /start чтобы вернуть её обратно",
            reply_markup=ReplyKeyboardRemove(),
        )


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
		'А Если наш, нажмите на кнопку "Первый Запуск" \n'
		'и следуйте дольнейшим укозаниям\n',
		reply_markup=get_base_reply_keyboard(),
	)

@log_errors
def do_join(update: Update, context: CallbackContext):

	update.message.reply_text(
		text='Вход Подтвержден ! \n\n'
		'Подтверждение требуется тоько один раз\n'
		'Теперь вы можете осуществлять Запросы\n',
		reply_markup=get_req_reply_keyboard()	
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
		reply_markup=get_base_inline_keyboard()	
	)

@log_errors
def do_req(update: Update, context: CallbackContext):
	update.message.reply_text(
		text='Покачто нет данных ! \n\n'
		'Обратись в администрацию\n',
		reply_markup=get_req_reply_keyboard()	
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
		join_hendler = MessageHandler(Filters.text(BUTTON_JION), do_join)
		help_hendler = MessageHandler(Filters.text(BUTTON_HELP), do_help)
		req_hendler = MessageHandler(Filters.text(BUTTON_REQ), do_help)
		
		#message_hendler = MessageHandler(Filters.text, do_echo)
		buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler)
		updater.dispatcher.add_handler(start_hendler)
		updater.dispatcher.add_handler(join_hendler)
		updater.dispatcher.add_handler(help_hendler)
		updater.dispatcher.add_handler(req_hendler)
		#updater.dispatcher.add_handler(message_hendler)


		# launching of infinite in going data
		updater.start_polling()
		updater.idle()