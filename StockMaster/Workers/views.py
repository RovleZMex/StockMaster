from django.shortcuts import render
from Product.models import Product

# Create your views here.
def store(request):
    products = Product.objects.all()
    print("Products:", products)
    context = {'products': products}
    return render(request,'store/store.html')