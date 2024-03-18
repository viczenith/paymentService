# money_transfer/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('moneyApp.urls')),
    path('transactions/', include('moneyApp.urls')),
    path('history/', include('moneyApp.urls')),
    path('profile/', include('moneyApp.urls')),
    path('register/', include('moneyApp.urls')),
    path('logout/', include('moneyApp.urls')),
    path('login/', include('moneyApp.urls')),

    path('deposit_money/', include('moneyApp.urls')),
    path('withdraw_money/', include('moneyApp.urls')),
    path('change-currency/', include('moneyApp.urls')),

    path('create_payment_requests/', include('moneyApp.urls')),
    path('view_payment_requests/', include('moneyApp.urls')),
    path('accept_payment_request/<int:pk>/', include('moneyApp.urls')),
    path('reject_payment_request/<int:pk>/', include('moneyApp.urls')),
]
