import calendar
import datetime
import json
import unicodedata

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render, get_object_or_404, redirect

from InputHistory.models import InputOrder, InputOrderItem
from Product.models import Product


@login_required(login_url='login')
def Inventory(request):
    """
    Render the inventory page with products filtered by the search query.

    Args:
        request: HTTP request object.

    Returns:
        Rendered HTML page with filtered products.

    """
    allProducts = Product.objects.all().order_by('name')

    searchQuery = ''

    searchCondition = Q()

    searchQuery = request.GET.get('search', '')

    if searchQuery:
        searchCondition = searchCondition & Q(name__icontains=searchQuery) | Q(SKU__icontains=searchQuery)

    filteredProducts = allProducts.filter(searchCondition)

    paginator = Paginator(filteredProducts, 5)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    return render(request, 'inventory.html', {'products': products, 'searchQuery': searchQuery})


@login_required(login_url='login')
def FilterInventory(request):
    """
    Filter the products in the inventory based on different criteria.

    Args:
        request: HTTP request object.

    Returns:
        Rendered HTML page with filtered products.

    """
    searchQuery = request.GET.get("search")
    category = request.GET.get("category")
    stock = request.GET.get("stock")

    allProducts = Product.objects.all()

    if searchQuery:
        searchQuery_normalized = RemoveAccents(searchQuery).lower()
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
    """
    Render the 'add-product' page and process the form data for adding products.

    Args:
        request: HTTP request object.

    Returns:
        Rendered 'add-product' page.

    """
    allProducts = Product.objects.all()

    if request.method == "POST":
        print(request.POST.getlist("productname"))  # GETS THE LIST OF PRODUCTS
        print(request.POST.getlist("quantity"))  # GETS THE LIST OF QUANTITIES
    context = {'products': allProducts}
    return render(request, 'add-product.html', context)


@login_required(login_url='login')
def EditProduct(request, productid):
    """
    Render the product edit page and process the form data for updating product information.

    Args:
        request: HTTP request object.
        productid: ID of the product to be edited.

    Returns:
        Rendered product edit page.

    """
    product = get_object_or_404(Product, id=productid)
    if request.method == "POST":
        product.name = request.POST.get("nombreProducto")
        product.quantity = request.POST.get("cantidadProducto")
        if len(request.FILES) != 0:
            product.image = request.FILES['imagenProducto']
        product.category = MapCategory(request.POST.get("categoriaProducto"))
        product.isExternal = request.POST.get('compradoPorFuera') == 'on'
        product.threshold = request.POST.get("bajoUmbralProducto")
        product.price = request.POST.get("productPrice")
        product.save()

    context = {'product': product,
               'ind': productid}

    return render(request, 'product-edit.html', context)

@login_required(login_url='login')
def deleteProduct(request, product_id):
    """
    Deletes item from database.

    Args:
        request: HTTP request object.
        product_id: ID of the product.

    Returns:
        Redirects to the inventory url after deleting item
    """
    if request.method == 'POST' and request.POST.get('method') == 'DELETE':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return redirect('inventory')


@login_required(login_url='login')
def ProductGraph(request, productid):
    """
    Render the product graph page with historical data of the product.

    Args:
        request: HTTP request object.
        productid: ID of the product.

    Returns:
        Rendered product graph page.

    """
    product = get_object_or_404(Product, id=productid)
    productHistory = product.history.filter(history_date__month=datetime.datetime.now().month,
                                            history_date__year=datetime.datetime.now().year)
    labels = []
    quantities = []
    prices = []
    for historicProduct in reversed(productHistory):
        labels.append(historicProduct.history_date.strftime('%d'))
        quantities.append(historicProduct.quantity)
        prices.append(historicProduct.price)
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    filteredLabels, filteredQuantities = AddLastDate(labels, quantities,
                                                     month, year, product, "quantity")
    filteredLabels, filteredPrices = AddLastDate(labels, prices,
                                                 month, year, product, "price")

    filteredLabels, filteredQuantities = FilterSameDates(filteredLabels, filteredQuantities)
    filteredLabels, filteredPrices = FilterSameDates(filteredLabels, filteredPrices)

    context = {
        'years': range(2023, 2074),
        'product': product,
        'data': json.dumps(filteredQuantities),
        'labels': ','.join(filteredLabels),
        'priceData': json.dumps(filteredPrices),
    }
    return render(request, 'product-graph.html', context)


@login_required(login_url='login')
def ProductDetails(request, productid):
    """
    Renders the product details page for a specific product.

    Args:
        request (HttpRequest): The HTTP request.
        productid (int): The ID of the product.

    Returns:
        HttpResponse: The rendered product details page with information about the specified product.
    """
    product = get_object_or_404(Product, id=productid)
    context = {
        'product': product
    }
    return render(request, 'product-details.html', context)


@login_required(login_url='login')
def GetProductPriceData(request):
    """
    Retrieve product price data for a specific month and year.

    Args:
        request: HTTP request object.

    Returns:
        JSON response with the product price data.

    """
    if request.method == "POST":
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))
        productid = request.POST.get("productid")
        product = Product.objects.get(id=productid)

        prices = []
        labels = []
        if datetime.datetime.now().month == month:
            daysRange = range(1, datetime.datetime.now().day + 1)
        elif month > datetime.datetime.now().month or year > datetime.datetime.now().year:
            daysRange = range(0)
        else:
            daysRange = range(1, calendar.monthrange(year, month)[1] + 1)
        for day in daysRange:
            tempDate = datetime.date(year, month, day)
            labels.append(f"Día {day}")
            try:
                if datetime.datetime.now().day == day and datetime.datetime.now().month == month and datetime.datetime.now().year == year:
                    prices.append(product.price)
                else:
                    prices.append(product.history.as_of(tempDate).price)
            except ObjectDoesNotExist:
                if len(prices) >= 1:
                    prices.append(prices[-1])
                else:
                    prices.append(0)

        return JsonResponse({
            'success': True,
            'data': json.dumps(prices),
            'labels': ','.join(labels),
        })


@login_required(login_url='login')
def GetProductQuantityData(request):
    """
    Retrieve product quantity data for a specific month and year.

    Args:
        request: HTTP request object.

    Returns:
        JSON response with the product quantity data.

    """
    if request.method == "POST":
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))
        productid = request.POST.get("productid")
        product = Product.objects.get(id=productid)
        labels = []
        quantities = []

        if datetime.datetime.now().month == month:
            daysRange = range(1, datetime.datetime.now().day + 1)
        elif month > datetime.datetime.now().month or year > datetime.datetime.now().year:
            daysRange = range(0)
        else:
            daysRange = range(1, calendar.monthrange(year, month)[1] + 1)
        for day in daysRange:
            tempDate = datetime.date(year, month, day)
            labels.append(f"Día {day}")
            try:
                if datetime.datetime.now().day == day and datetime.datetime.now().month == month and datetime.datetime.now().year == year:
                    quantities.append(product.quantity)
                else:
                    quantities.append(product.history.as_of(tempDate).quantity)
            except ObjectDoesNotExist:
                if len(quantities) >= 1:
                    quantities.append(quantities[-1])
                else:
                    quantities.append(0)

        return JsonResponse({
            'success': True,
            'data': json.dumps(quantities),
            'labels': ','.join(labels),
        })
    return JsonResponse({'error': 'Error, verifica los datos.'}, status=400)


@login_required(login_url='login')
def AddProduct(request):
    """
    Add a new product based on the form data.

    Args:
        request: HTTP request object.

    Returns:
        JSON response indicating the success or failure of the product addition.

    """
    if request.method == "POST":
        if VerifyProductForm(request):
            name = request.POST.get('nombreProducto')
            quantity = 0
            threshold = request.POST.get('bajoUmbralProducto')
            category = request.POST.get('categoriaProducto')
            SKU = request.POST.get('SKU')
            price = float(request.POST.get('price'))
            is_external = True if request.POST.get('compradoPorFuera') == 'true' else False
            new_product = Product.objects.create(
                name=name,
                quantity=quantity,
                threshold=threshold,
                category=category,
                isExternal=is_external,
                SKU=SKU,
                price=price,
            )
            if 'imagenProducto' in request.FILES:
                imagen = request.FILES['imagenProducto']
                file_name = default_storage.save(imagen.name, imagen)
                new_product.image = file_name
                new_product.save()

            return JsonResponse({
                'success': True,
                'newProduct': {
                    'name': new_product.name,
                    'price': new_product.price,
                    'isExternal': new_product.isExternal,
                    'sku': new_product.SKU
                }
            })
    return JsonResponse({'error': 'Error, verifica los datos.'}, status=400)


@login_required(login_url='login')
def HandleProductData(request):
    """
    Handle the data for multiple products received from the frontend.

    Args:
        request: HTTP request object.

    Returns:
        JSON response indicating the success or failure of handling the product data.

    """
    if request.method == 'POST':
        products_data = request.POST.get('productsData')  # Aquí se obtienen los datos de los productos del frontend

        products_data_list = json.loads(products_data)

        newOrder = InputOrder()
        newOrder.save()
        for product_data in products_data_list:
            VerifyAndUpdate(product_data)
            CreateOrderItem(product_data, newOrder)
        return JsonResponse({'message': 'Datos de productos recibidos con éxito'})
    else:
        return JsonResponse({'message': 'Error al procesar la solicitud'}, status=400)


def VerifyProductForm(request):
    """
    Verify if the product form contains the required fields.

    Args:
        request: HTTP request object.

    Returns:
        Boolean indicating whether the form is valid.

    """
    if 'nombreProducto' in request.POST:
        if 'price' in request.POST:
            if 'SKU' in request.POST:
                return True
    return False


def VerifyAndUpdate(product):
    """
    Verify and update product information.

    Args:
        product: Dictionary containing product information.

    Returns:
        None

    """
    if product["productName"] == "":
        return
    name1 = DeleteLeftFromSequence(product["productName"], " - ").strip()
    dbProduct = Product.objects.get(SKU=name1)
    dbProduct.isExternal = product['isExternal']
    if product['quantityType'] == "unidades":
        dbProduct.quantity += int(product['quantity'])
        dbProduct.price = product['price']
    else:
        dbProduct.quantity += int(product['quantity']) * int(product['unitsPerBox'])
        dbProduct.price = int(product['price']) / int(product['unitsPerBox'])
    dbProduct.save()


def CreateOrderItem(product_data, order):
    """
    Create an order item based on the product data.

    Args:
        product_data: Dictionary containing product data.
        order: InputOrder object.

    Returns:
        None

    """
    if product_data["productName"] == "":
        return
    product = Product.objects.get(SKU=DeleteLeftFromSequence(product_data["productName"], " - ").strip())
    if product_data['quantityType'] == "unidades":
        quantity = int(product_data['quantity'])
    else:
        quantity = int(product_data['quantity']) * int(product_data['unitsPerBox'])
    InputOrderItem.objects.create(
        product=product,
        quantity=quantity,
        inputOrder=order
    )


def DeleteLeftFromSequence(text, sequence):
    """
    Delete a sequence from the left side of a text.

    Args:
        text: Text string.
        sequence: Sequence to be deleted.

    Returns:
        Modified text string.

    """
    index = text.rfind(sequence)
    if index != -1:
        return text[(index + len(sequence)):]
    else:
        return text


def RemoveAccents(input_str):
    """
    Remove accents from a given string.

    Args:
        input_str: Input string.

    Returns:
        String without accents.
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def FilterSameDates(labels, otherList):
    """
    Filter out the same dates from the lists of labels and other data.

    Args:
        labels: List of labels.
        otherList: List of other data.

    Returns:
        Filtered lists of labels and other data.

    """
    filteredLabels = []
    filteredPrices = []
    if len(labels) > 1:
        for i in range(len(labels) - 1):
            if labels[i] != labels[i + 1]:
                filteredLabels.append(labels[i])
                filteredPrices.append(otherList[i])
        filteredLabels.append(labels[-1])
        filteredPrices.append(otherList[-1])
    else:
        filteredLabels = labels
        filteredPrices = otherList
    print(labels)
    return filteredLabels, filteredPrices


def AddLastDate(filteredLabels, filteredList, month, year, product, attribute):
    """
    Add the last date to the lists of labels and filtered data.

    Args:
        filteredLabels: List of labels.
        filteredList: List of filtered data.
        month: Current month.
        year: Current year.
        product: Product object.
        attribute: Attribute to be added.

    Returns:
        Modified lists of labels and filtered data.

    """
    filteredLabels = filteredLabels
    filteredList = filteredList
    if datetime.datetime.now().month == month:
        stringDay = str(datetime.datetime.now().day)
        if len(stringDay) == 1:
            filteredLabels.append(f"0{stringDay}")
        else:
            filteredLabels.append(stringDay)
        if attribute == "quantity":
            filteredList.append(product.quantity)
        elif attribute == "price":
            filteredList.append(product.price)
    else:
        stringDay = str(calendar.monthrange(year, month)[1])
        if len(stringDay) == 1:
            filteredLabels.append(f"0{stringDay}")
        else:
            filteredLabels.append(stringDay)
        lastDateOfMonth = datetime.datetime(year, month, calendar.monthrange(year, month)[1])
        try:
            lastProduct = product.history.as_of(lastDateOfMonth)
            if attribute == "quantity":
                filteredList.append(lastProduct.quantity)
            elif attribute == "price":
                filteredList.append(lastProduct.price)
        except Product.DoesNotExist:
            filteredLabels = []
            filteredList = []
    return filteredLabels, filteredList


def MapCategory(value):
    """
    Map a value to a specific category.

    Args:
        value: Value to be mapped.

    Returns:
        Mapped category.

    """
    categories = {'1': 'OFF',
                  '2': 'CLE',
                  '3': 'ELE',
                  '4': 'PLU'}
    return categories[value]
