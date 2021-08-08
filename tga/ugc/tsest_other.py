from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from django.conf import settings

def start(bot, update):
	# Сразу задаём первый вопрос, а ответ уже смотрим в первом обработчике
	update.message.reply_text('Привет! Ты хотел бы получить информацию об адресах наших учебных центров?')
	# Число-ключ в словаре states ConversationHandler
	# Оно указывает, что дальше на сообщения от этого пользователя должен отвечать обработчик states[1]
	# До этого момента обработчиков текстовых сообщений
	# для этого пользователя не было,
	# поэтому текстовые сообщения игнорировались
	return 1

def first_response(bot, update, user_data):
	# Ответ вопрос, заданный в /start
	answer = update.message.text
	if answer.lower() == 'да' or answer.lower() == 'yes':
		# Задаём новый вопрос, а ответ обрабатываем в обработчике 2
		update.message.reply_text('Тогда напиши, в каком городе ты проживаешь?')
		return 2
	else:
		update.message.reply_text('Ну как хочешь...')
		return ConversationHandler.END
	
	# Следующее текстовое сообщение
	# будет обработано обработчиком states[2]

def second_response(bot, update, user_data):
	# База данных всех адресов учебных центров
	address = {'Москва': 'Красная Пресня, 31',
			  'Санкт-Петербург': 'Невский проспект, 114'}    
	
	# Ответ на второй вопрос
	# Мы можем его сохранить его в базе данных или переслать куда-либо
	locality = update.message.text
	user_data['locality'] = locality
	
	answer_address = address.get(locality, 'Адрес не найден')
	update.message.reply_text('Твой центр находится по адресу:')
	update.message.reply_text(answer_address)
	
	# Константа, означающая конец диалога
	# Все обработчики из states и fallbacks становятся неактивными
	return ConversationHandler.END 
	

def stop(bot, update):
	update.message.reply_text("Жаль. А было бы интересно пообщаться. Хорошего дня!")
	return ConversationHandler.END
	
	
conv_handler = ConversationHandler(
	# Точка входа в диалог.
	# В данном случае — команда /start. Она задаёт первый вопрос.
	entry_points=[CommandHandler('start', start)],
	
	# Словарь состояний внутри диалога. 
	# Наш вариант с двумя обработчиками,
	# фильтрующими текстовые сообщения.
	states={
	# Функция читает ответ на первый вопрос и задаёт второй.
	1: [MessageHandler(Filters.text, first_response, pass_user_data=True)],
	# Функция читает ответ на второй вопрос и завершает диалог.
	2: [MessageHandler(Filters.text, second_response, pass_user_data=True)]
	},
	
	# Точка прерывания диалога. В данном случае — команда /stop.
	fallbacks=[CommandHandler('stop', stop)]
)

updater = Updater(settings.TOKEN)

dp = updater.dispatcher

dp.add_handler(conv_handler)
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('stop', stop))

updater.start_polling()

updater.idle()