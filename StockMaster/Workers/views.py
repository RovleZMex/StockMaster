from django.shortcuts import render
from Product.models import Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
def store(request):
    products = Product.objects.all()  # REGRESA LAS INSTANCIAS DE TODOS LOS PRODUCTOS EN LA BASE DE DATOS
    context = {
        "products": products,
    }
    product_count = products.count()
    return render(request, 'store/store.html', context)
