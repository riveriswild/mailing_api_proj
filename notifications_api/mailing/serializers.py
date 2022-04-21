from rest_framework import serializers
from .models import Client, Mailing, Message


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = ('id', 'msg_text', 'date_start', 'date_end', 'time_start', 'time_end', 'tag_filter', 'operator_code_filter')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'phone_number', 'operator_code', 'timezone', 'tag')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'time_sent', 'msg_status', 'client', 'mailing')


class StatisticsMailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = ('id', 'dispatched', 'all_messages', 'sent_messages')



