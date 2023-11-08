# views.py
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Product.models import Product


@login_required(login_url='login')
def inventory_category_chart(request):
    categories = ['Eléctrico', 'Plomería', 'Oficina', 'Limpieza']
    quantities = [0, 0, 0, 0]
    for product in Product.objects.all():
        if product.category == "ELE":
            quantities[0] += 1
        elif product.category == "PLU":
            quantities[1] += 1
        elif product.category == "OFF":
            quantities[2] += 1
        elif product.category == "CLE":
            quantities[3] += 1
    context = {
        'quantities': json.dumps(quantities),
        'categories': ','.join(categories)
    }
    return render(request, 'inventory_category_chart.html', context)
