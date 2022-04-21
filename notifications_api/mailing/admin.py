from django.contrib import admin
from .models import Mailing, Client, Message


class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_start', 'date_end', 'time_start', 'time_end', 'dispatched', 'all_messages', 'sent_messages')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'msg_status', 'mailing', 'client')
    list_filter = ['msg_status']

class ClientAdmin(admin.ModelAdmin) :
    list_display = ('id', 'phone_number', 'operator_code', 'timezone')


admin.site.register(Mailing, MailingAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Client, ClientAdmin)


# Register your models here.
