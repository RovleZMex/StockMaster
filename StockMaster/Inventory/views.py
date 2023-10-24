from django.shortcuts import render
from Product.models import Product

# Create your views here.

def inventory(request):
    products = Product.objects.all()
    return render(request, 'inventory.html', {'products': products})