from django.contrib import admin
from .models import Product
from .models import Worker, OutputOrder, OutputOrderItem

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'SKU', 'price', 'quantity', 'image', 'threshold', 'category', 'isExternal')


admin.site.register(Product, ProductAdmin)
admin.site.register(Worker)
admin.site.register(OutputOrder)
admin.site.register(OutputOrderItem)
