from django.contrib import admin

from .forms import ProfileForm
from .models import Profile
from .models import Message
from .models import Departments
from .models import Requests
from .models import StatusedBy
from .models import Faq
from .models import NeedTypes

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('external_id', 'name','department','status', 'created_at')
	list_display_links = ('department','status')
	search_fields = ('external_id','name', 'department')
	form = ProfileForm

@admin.register(Requests)
class RequestsAdmin(admin.ModelAdmin):
	list_display = ('reply_to_message_id', 'profile', 'department', 'status', 'need_type',
		'need', 'amount', 'send_at')
	list_display_links = ('status','department')
	
@admin.register(StatusedBy)
class StatusedByAdmin(admin.ModelAdmin):
	list_display = ('profile','created_at')

@admin.register(Departments)
class DepartmentsAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'location')
	list_display_links= ('location', 'title')

@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
	list_display = ('title', 'desc')
	list_display_links= ('title', 'desc')

@admin.register(NeedTypes)
class NeedTypesAdmin(admin.ModelAdmin):
	list_display = ('id', 'title')
	list_display_link= ('title')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ('id', 'profile', 'text','created_at')
	list_display_links= ('id', 'profile')

	# def get_query_set(self, request):
	# 	return

