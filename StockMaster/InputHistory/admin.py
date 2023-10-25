from django.contrib import admin
from .models import InputOrder, InputOrderItem
# Register your models here.
admin.site.register(InputOrder)
admin.site.register(InputOrderItem)