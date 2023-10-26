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
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
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
    workers = Worker.objects.all()

    paginator = Paginator(workers, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, 'workers.html', context)
