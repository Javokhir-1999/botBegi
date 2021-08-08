from django.db import models

class Departments(models.Model):
	title = models.TextField(
		verbose_name="Название",
	)
	location = models.TextField(
		verbose_name="Адресс",
	)
	def __str__(self):
		return f'{self.title}'

	class Meta:
		verbose_name = "Отдел"
		verbose_name_plural = "Отделы"

class NeedTypes(models.Model):
	title = models.TextField(
		verbose_name="title",
	)
	def __str__(self):
		return f'{self.title}'

	class Meta:
		verbose_name = "Нужда"
		verbose_name_plural = "Нужды"

class StatusedBy(models.Model):
	profile = models.ForeignKey(
		to='ugc.Profile',
		verbose_name="Модератор",
		on_delete=models.PROTECT,
	)
	created_at = models.DateTimeField(
		verbose_name="Время Изменения",
		auto_now_add = True,
	)

	class Meta:
		verbose_name = "TG История"
		verbose_name_plural = "TG Истории"

class Profile(models.Model):
	REQUESTED ='REQUESTED'
	JOINED ='JOINED'
	BLOCKED ='BLOCKED'
	ADMIN ='ADMIN'
	STATUS_CHOICES = [
		(REQUESTED, 'REQUESTED'),
		(JOINED, 'JOINED'),
		(BLOCKED, 'BLOCKED'),
		(ADMIN, 'ADMIN'),
	]

	external_id = models.PositiveIntegerField(
		verbose_name="Телеграм ID",
		unique=True,
	)
	name = models.TextField(
		verbose_name ="Имя",
	)
	status = models.TextField(
		max_length=20,
		verbose_name="Статус",
		choices=STATUS_CHOICES,
		default=REQUESTED,
	)
	department = models.ForeignKey(
		to='ugc.Departments',
		verbose_name="Отдел",
		on_delete=models.PROTECT,
	)
	created_at = models.DateTimeField(
		verbose_name="Время создания",
		auto_now_add = True,
	)

	def __str__(self):
		return f'#{self.external_id} {self.name}'

	class Meta:
		verbose_name = "Профиль"
		verbose_name_plural = "Профили"

class Requests(models.Model):
	REQUESTED ='REQUESTED'
	ACCEPTED ='ACCEPTED'
	REJECTED ='REJECTED'
	STATUS_CHOICES = [
		(REQUESTED, 'REQUESTED'),
		(ACCEPTED, 'ACCEPTED'),
		(REJECTED, 'REJECTED'),
	]

	profile = models.ForeignKey(
		to='ugc.Profile',
		verbose_name="Отправитель Зопроса",
		on_delete=models.PROTECT,
	)
	department = models.ForeignKey(
		to='ugc.Departments',
		verbose_name="Отдел",
		on_delete=models.PROTECT,
	)
	message_id = models.IntegerField(
		verbose_name="ID Сообщения от Админ ",
		unique=True,
		default=100,
	)
	reply_to_message_id = models.IntegerField(
		verbose_name="ID Запроса",
		unique=True,
		default=200,
	)
	status = models.TextField(
		max_length=20,
		verbose_name="Статус",
		choices=STATUS_CHOICES,
		default=REQUESTED,
	)
	need_type = models.ForeignKey(
		to='ugc.NeedTypes',
		verbose_name="Тип Нужды",
		on_delete=models.PROTECT,
	)
	need = models.TextField(
		verbose_name="Описание Нужды",
	)
	amount = models.TextField(
		verbose_name="Сумма",
	)
	send_at = models.DateTimeField(
		verbose_name="Время Отправки",
		auto_now_add = True,
	)
	def __str__(self):
		return f'Сообщение {self.pk} {self.profile}'

	class Meta:
		verbose_name = "Зопрос"
		verbose_name_plural = "Зопросы"	

class Faq(models.Model):
	title = models.TextField(
		verbose_name="Тайтл вопроса",
	)
	desc = models.TextField(
		verbose_name="Описание",
	)
	def __str__(self):
		return f'{self.title}'

class Message(models.Model):
	profile = models.ForeignKey(
		to='ugc.Profile',
		verbose_name="Профиль",
		on_delete=models.PROTECT,
	)
	text = models.TextField(
		verbose_name="Text",
	)
	created_at = models.DateTimeField(
		verbose_name="Время Отправки",
		auto_now_add = True,
	)
	def __str__(self):
		return f'Сообщение {self.pk} {self.profile}'

	class Meta:
		verbose_name = "Сообщение"
		verbose_name_plural = "Сообщения"	