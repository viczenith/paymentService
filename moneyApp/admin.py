from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(CustomUserGroups)
admin.site.register(Profile)
admin.site.register(Transaction)