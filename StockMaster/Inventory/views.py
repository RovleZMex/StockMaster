from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Product.models import Product


# Create your views here.

@login_required(login_url='login')
def inventory(request):
    products = Product.objects.all()
    return render(request, 'inventory.html', {'products': products})
