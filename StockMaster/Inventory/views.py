import unicodedata

from Product.models import Product
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect


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
        searchCondition = searchCondition & Q(name__icontains=searchQuery) | Q(SKU__icontains=searchQuery)

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


@login_required(login_url='login')
def AddProducts(request):
    allProducts = Product.objects.all()

    if request.method == "POST":
        print(request.POST.getlist("productname"))  # GETS THE LIST OF PRODUCTS
        print(request.POST.getlist("quantity"))  # GETS THE LIST OF QUANTITIES
    context = {'products': allProducts}
    return render(request, 'add-product.html', context)


@login_required(login_url='login')
def EditProduct(request, productid):
    product = get_object_or_404(Product, id=productid)
    if request.method == "POST":
        product.name = request.POST.get("nombreProducto")
        product.quantity = request.POST.get("cantidadProducto")
        if len(request.FILES) != 0:
            product.image = request.FILES['imagenProducto']
        product.category = mapCategory(request.POST.get("categoriaProducto"))
        product.isExternal = request.POST.get('compradoPorFuera') == 'on'
        product.threshold = request.POST.get("bajoUmbralProducto")
        product.save()
        return redirect('inventory')

    context = {'product': product,
               'ind': productid}

    return render(request, 'product-edit.html', context)


# used by AJAX to create a new product
def add_product(request):
    if request.method == "POST":
        print(request.POST.get("nombreProducto"))
        # Get data from request
        if verifyProductForm(request):
            name = request.POST.get('nombreProducto')
            quantity = 0
            threshold = request.POST.get('bajoUmbralProducto')
            category = request.POST.get('categoriaProducto')
            SKU = request.POST.get('SKU')
            price = float(request.POST.get('price'))
            is_external = True if request.POST.get('compradoPorFuera') == 'true' else False
            # Crear un nuevo objeto Product
            new_product = Product.objects.create(
                name=name,
                quantity=quantity,
                threshold=threshold,
                category=category,
                isExternal=is_external,
                SKU=SKU,
                price=price,
            )
            print('AAAAAA')
            if 'imagenProducto' in request.FILES:
                print('AAAAAA')
                imagen = request.FILES['imagenProducto']
                # Guardar la imagen en el sistema de archivos
                file_name = default_storage.save(imagen.name, imagen)
                # Asociar la imagen guardada con el producto recién creado
                new_product.image = file_name
                new_product.save()

            # Puedes devolver los datos del producto recién creado en formato JSON
            return JsonResponse({
                'success': True,
                'newProduct': {
                    'name': new_product.name,
                    'price': new_product.price,
                    'isExternal': new_product.isExternal
                }
            })
    return JsonResponse({'error': 'Error, verifica los datos.'}, status=400)


def verifyProductForm(request):
    if 'nombreProducto' in request.POST:
        if 'price' in request.POST:
            if 'SKU' in request.POST:
                return True
    return False


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def mapCategory(valor):
    categorias = {'1': 'OFF',
                  '2': 'CLE',
                  '3': 'ELE',
                  '4': 'PLU'}
    return categorias[valor]
