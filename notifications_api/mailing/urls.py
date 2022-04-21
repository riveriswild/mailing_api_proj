from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'mailings', MailingViewSet)
router.register(r'statistics', MailingStatsView)

urlpatterns = [
    path('api/', include(router.urls)),
    # path('api-auth/', include("rest_framework.urls", namespace="rest_framework")),
]