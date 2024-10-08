import unicodedata
from datetime import datetime

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

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
        return redirect("dashboard")  # The user is already signed in

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(
            request, username=username, password=password
        )  # Does the user exist?
        if user is not None:
            login(request, user)  # If it does, log them in
            return redirect("dashboard")
        else:
            return redirect("login")  # If it doesn't, reload the page

    return render(request, "login.html")


# Simply used to log out the user and redirect.
@login_required(login_url="login")
def LogoutPage(request):
    """
    Logs out the user and redirects to the login page.

    Returns:
        Redirection to the login page.
    """
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def Dashboard(request):
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
    noStockProducts = Product.objects.filter(
        quantity=0
    ).count()  # Filter and count the amount of products out of stock

    categoryData = [
        Product.objects.filter(category="ELE").count(),
        Product.objects.filter(category="PLU").count(),
        Product.objects.filter(category="OFF").count(),
        Product.objects.filter(category="CLE").count(),
    ]

    lastInputOrders = InputOrder.objects.all().order_by("-date_created")[:5]
    lastOutputOrders = OutputOrder.objects.all().order_by("-date_created")[:5]

    context = {
        "allProducts": allProducts.count(),
        "goodStockProducts": allProducts.count() - noStockProducts - lowStockProducts,
        "lowStockProducts": lowStockProducts,
        "noStockProducts": noStockProducts,
        "productData": [
            allProducts.count() - noStockProducts - lowStockProducts,
            lowStockProducts,
            noStockProducts,
        ],
        "categoryData": categoryData,
        "lastInputOrders": lastInputOrders,
        "lastOutputOrders": lastOutputOrders,
    }
    return render(request, "dashboard.html", context)


@login_required(login_url="login")
def Workers(request):
    """
    Displays a list of workers and provides a search functionality.

    Returns:
        A rendered workers page with a list of workers and search functionality.
    """
    searchQuery = request.GET.get("search")
    if searchQuery:
        search_query_normalized = "%" + RemoveAccents(searchQuery).lower() + "%"

        filtered_workers = Worker.objects.raw(
            """SELECT * FROM Workers_worker
                                            WHERE name LIKE %s""",
            [search_query_normalized],
        )
        paginator = Paginator(
            filtered_workers, 10
        )  # Muestra 10 trabajadores por página
    else:
        worker_list = Worker.objects.raw("SELECT * FROM Workers_worker")
        paginator = Paginator(worker_list, 10)  # Muestra 10 trabajadores por página

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}

    return render(request, "workers.html", context)


@login_required(login_url="login")
def workerDetails(request, employeeNumber):
    worker = get_object_or_404(Worker, employeeNumber=employeeNumber)

    # output_orders = worker.outputorder_set.all().order_by("-date_created")
    output_orders = OutputOrder.objects.raw(
        """
        SELECT * FROM OutputHistory_outputorder
        JOIN Workers_worker ON Workers_worker.id = OutputHistory_outputorder.worker_id 
        WHERE Workers_worker.id = %s
        ORDER BY date_created DESC""",
        [worker.id],
    )

    context = {
        "years": range(2023, datetime.now().year + 1),
        "worker": worker,
        "output_orders_page": output_orders,
        "ind": employeeNumber,
    }

    return render(request, "workerDetails.html", context)


@login_required(login_url="login")
def EditWorker(request, employeeNumber):
    """
    Render the worker edit page and process the form data for updating worker information.

    Args:
        request: HTTP request object.
        employeeNumber: Employee number of the worker to be edited.

    Returns:
        Rendered worker edit page or redirects to worker details.
    """
    worker = get_object_or_404(Worker, employeeNumber=employeeNumber)

    if request.method == "POST":
        # Process form data and update worker information
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Workers_worker SET name = %s, workArea = %s, employeeNumber = %s, employeePassword = %s WHERE employeeNumber = %s",
                [
                    request.POST.get("nombreTrabajador"),
                    request.POST.get("areaTrabajo"),
                    int(request.POST.get("employeeNumber")),
                    request.POST.get("employeePassword"),
                    employeeNumber,
                ],
            )
        return redirect("workers")

    context = {"worker": worker, "ind": employeeNumber}

    return render(request, "workerEdit.html", context)


@login_required(login_url="login")
def deleteWorker(request, employeeNumber):
    """
    Deletes a worker from the database.

    Args:
        request: HTTP request object.
        employeeNumber: Employee number of the worker to be deleted.

    Returns:
        Redirects to the workers list page after deleting the worker.
    """
    if request.method == "POST" and request.POST.get("method") == "DELETE":
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Workers_worker WHERE employeeNumber = %s", [employeeNumber]
            )
        return redirect("workers")


class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["name", "employeeNumber", "workArea", "employeePassword"]

    def clean_employeeNumber(self):
        employeeNumber = self.cleaned_data.get("employeeNumber")
        if Worker.objects.filter(employeeNumber=employeeNumber).exists():
            raise ValidationError("Este numero de empleado ya existe.")
        return employeeNumber


def addWorker(request):
    if request.method == "POST":
        form = WorkerForm(request.POST)
        if form.is_valid():
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO Workers_worker (name, employeeNumber, workArea, employeePassword) VALUES 
                    (%s, %s, %s, %s)""",
                    [
                        request.POST.get("name"),
                        int(request.POST.get("employeeNumber")),
                        request.POST.get("workArea"),
                        request.POST.get("employeePassword"),
                    ],
                )
            return redirect(
                "workers"
            )  # Redirect to the workers list page after adding a worker
    else:
        form = WorkerForm()

    return render(request, "add_worker.html", {"form": form})


def GetWorkerOrdersMonth(request):
    if request.method == "POST":
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))
        employeeNumber = int(request.POST.get("employeeNumber"))

        allOrders = OutputOrder.objects.filter(worker__employeeNumber=employeeNumber)
        filteredOrders = []

        for order in allOrders:
            if order.date_created.month == month and order.date_created.year == year:
                order_data = {
                    "id": order.id,
                    "date_created": order.date_created.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),  # Formatear la fecha como string
                    "items": [
                        {
                            "product": {"name": item.product.name},
                            "quantity": item.quantity,
                        }
                        for item in order.GetItems()
                    ],
                    "total": order.GetTotal(),
                }
                filteredOrders.append(order_data)
        print(filteredOrders)
        return JsonResponse({"success": True, "data": filteredOrders})
    return JsonResponse(
        {
            "success": False,
        }
    )


def RemoveAccents(input_str):
    """
    Removes accents from a string.

    Args:
        input_str (str): The string from which to remove accents.

    Returns:
        str: The string without accents.
    """
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])
