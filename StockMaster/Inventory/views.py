
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Product.models import Product
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import F
import unicodedata



@login_required(login_url='login')
def inventory(request):
    allProducts = Product.objects.all().order_by('name')

    # Initialize the empty search variable
    searchQuery = ''

    # Build the search condition using the selected filter
    searchCondition = Q()

    # Obtain the search value by consulting GET
    searchQuery = request.GET.get('search', '')

    # If a search query is obtain, apply to the search condition
    if searchQuery:
        searchCondition = searchCondition & Q(name__icontains=searchQuery)

    # Filter products according to the search condition and threshold filter
    filteredProducts = allProducts.filter(searchCondition)

    paginator = Paginator(filteredProducts, 5)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    return render(request, 'inventory.html', {'products': products, 'searchQuery': searchQuery})


def filterInventory(request):
    searchQuery = request.GET.get("search")
    category = request.GET.get("category")
    stock = request.GET.get("stock")

    allProducts = Product.objects.all()

    if searchQuery:
        searchQuery_normalized = remove_accents(searchQuery).lower()
        allProducts = allProducts.filter(
            Q(name__icontains=searchQuery_normalized) | Q(SKU__icontains=searchQuery_normalized)
        )

    if category:
        allProducts = allProducts.filter(category=category)

    if stock == "low-stock-inventory":
        lowStock = []
        for product in allProducts:
            if product.isLowStock() and product.quantity > 0:
                lowStock.append(product)
        allProducts = lowStock
    elif stock == "good-stock-inventory":
        goodStock = []
        for product in allProducts:
            if not product.isLowStock():
                goodStock.append(product)
        allProducts = goodStock
    elif stock == "no-stock-inventory":
        noStock = []
        for product in allProducts:
            if product.quantity == 0:
                noStock.append(product)
        allProducts = noStock

    paginator = Paginator(allProducts, 5)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    return render(request, 'inventory.html', {
        'products': products,
    })


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])