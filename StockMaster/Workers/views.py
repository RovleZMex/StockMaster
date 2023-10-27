from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from Product.models import Product
from django.db.models import Q

def store(request):
    query = request.GET.get('query', '')
    product_list = Product.objects.filter(Q(name__icontains=query))
    paginator = Paginator(product_list, 9)  # Show 10 products per page

    page = request.GET.get('page') or 1
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "product_count": products.paginator.count,
        "query": query,
    }
    return render(request, 'store/store.html', context)
