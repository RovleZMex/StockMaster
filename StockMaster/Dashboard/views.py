import unicodedata

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from InputHistory.models import InputOrder
from OutputHistory.models import OutputOrder
from Product.models import Product
from Workers.models import Worker


# Create your views here.
def LoginPage(request):
    """
    Displays the login page or redirects to the dashboard if the user is already authenticated.

    Returns:
        A rendered login page or a redirection to the dashboard if the user is already logged in.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')  # The user is already signed in

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)  # Does the user exist?
        if user is not None:
            login(request, user)  # If it does, log them in
            return redirect('dashboard')
        else:
            return redirect('login')  # If it doesn't, reload the page

    return render(request, 'login.html')


# Simply used to log out the user and redirect.
@login_required(login_url='login')
def LogoutPage(request):
    """
    Logs out the user and redirects to the login page.

    Returns:
        Redirection to the login page.
    """
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """
    Displays the dashboard with various statistics and data about products, orders, and more.

    Returns:
        A rendered dashboard page with relevant statistics and data.
    """
    allProducts = Product.objects.all()
    lowStockProducts = 0
    for product in allProducts:  # We count the amount products that are in low stock.
        if product.quantity <= product.threshold:
            lowStockProducts += 1
    noStockProducts = Product.objects.filter(quantity=0).count()  # Filter and count the amount of products out of stock

    categoryData = [Product.objects.filter(category='ELE').count(),
                    Product.objects.filter(category='PLU').count(),
                    Product.objects.filter(category='OFF').count(),
                    Product.objects.filter(category='CLE').count()]

    lastInputOrders = InputOrder.objects.all()[:5]
    lastOutputOrders = OutputOrder.objects.all()[:5]

    context = {'allProducts': allProducts.count(),
               'goodStockProducts': allProducts.count() - noStockProducts - lowStockProducts,
               'lowStockProducts': lowStockProducts,
               'noStockProducts': noStockProducts,
               'productData': [allProducts.count() - noStockProducts - lowStockProducts,
                               lowStockProducts,
                               noStockProducts],
               'categoryData': categoryData,
               'lastInputOrders': lastInputOrders,
               'lastOutputOrders': lastOutputOrders}
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def workers(request):
    """
    Displays a list of workers and provides a search functionality.

    Returns:
        A rendered workers page with a list of workers and search functionality.
    """
    searchQuery = request.GET.get('search')
    if searchQuery:
        search_query_normalized = remove_accents(searchQuery).lower()
        worker_list = Worker.objects.all()
        filtered_workers = []
        for worker in worker_list:
            if search_query_normalized in remove_accents(worker.name).lower():
                filtered_workers.append(worker)
        paginator = Paginator(filtered_workers, 5)  # Muestra 10 trabajadores por página
    else:
        worker_list = Worker.objects.all()
        paginator = Paginator(worker_list, 5)  # Muestra 10 trabajadores por página

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, 'workers.html', context)


def remove_accents(input_str):
    """
    Removes accents from a string.

    Args:
        input_str (str): The string from which to remove accents.

    Returns:
        str: The string without accents.
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
