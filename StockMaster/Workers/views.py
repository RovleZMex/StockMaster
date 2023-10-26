from django.shortcuts import render
from Product.models import Product


# Create your views here.
def store(request):
    products = Product.objects.all()  # REGRESA LAS INSTANCIAS DE TODOS LOS PRODUCTOS EN LA BASE DE DATOS
    context = {
        "products": products,
    }
    return render(request, 'store/store.html', context)
