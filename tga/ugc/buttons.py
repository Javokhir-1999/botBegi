from telegram import KeyboardButton
from telegram import InlineKeyboardButton
from telegram import ReplyKeyboardMarkup


BUTTON_JOIN = "Войти"
BUTTON_HELP = "Помощь"
BUTTON_REQ = "Запросить"
BUTTON_REREQ = "Отправить Запрос"
BUTTON_SEND = "Отправить"
BUTTON_BACK = "Назад"
BUTTON_CLOSE = "Отменить"

BUTTON_EXPORT = "Экспорт"
BUTTON_INFO = "Инфа"

CARTON = "Картонный цех 📦"
PAPER = "Бумажный цех 📜🧻"
SETT = "Брусчатка цех 🔶"

FOOD = "Еда 🍲"
COMMON = "Общие Нужды"
TOOLS = "Рабочие Принадлежности"
ADVANCE = "Аванс 💴"
FORWAY = "На Дорогу 🚕"

def get_base_reply_keyboard():
	keyboard = [
		[
			KeyboardButton(BUTTON_JOIN),
		],
	]
	return ReplyKeyboardMarkup(
		keyboard=keyboard,
		resize_keyboard=True,
	)
def get_base_admin_keyboard():
	keyboard = [
		[
			KeyboardButton(BUTTON_EXPORT),
			KeyboardButton(BUTTON_INFO),
		],
	]
	return ReplyKeyboardMarkup(
		keyboard=keyboard,
		resize_keyboard=True,
	)
def get_req_reply_keyboard():
	keyboard = [
		[
			KeyboardButton(BUTTON_REQ),
			# KeyboardButton(BUTTON_CLOSE),
		],
	]
	return ReplyKeyboardMarkup(
		keyboard=keyboard,
		resize_keyboard=True,
	)
def get_back_close_keyboard():
	keyboard = [
		[
			KeyboardButton(BUTTON_BACK),
			KeyboardButton(BUTTON_CLOSE),
		],
	]
	return ReplyKeyboardMarkup(
		keyboard=keyboard,
		resize_keyboard=True,
	)
def get_send_redo_keyboard():
	keyboard = [
		[
			KeyboardButton(BUTTON_SEND),
			KeyboardButton(BUTTON_CLOSE),
		],
	]
	return ReplyKeyboardMarkup(
		keyboard=keyboard,
		resize_keyboard=True,
	)