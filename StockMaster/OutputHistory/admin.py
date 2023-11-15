from django.contrib import admin

from .models import Worker, OutputOrder, OutputOrderItem

# Register your models here.

admin.site.register(Worker)
admin.site.register(OutputOrder)
admin.site.register(OutputOrderItem)
