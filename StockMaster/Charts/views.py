import calendar
import json
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render

from Product.models import Product


@login_required(login_url='login')
def ReportCharts(request):
    categories = ['Eléctrico', 'Plomería', 'Oficina', 'Limpieza']
    quantities = [0, 0, 0, 0]
    for product in Product.objects.all():
        if product.category == "ELE":
            quantities[0] += product.quantity
        elif product.category == "PLU":
            quantities[1] += product.quantity
        elif product.category == "OFF":
            quantities[2] += product.quantity
        elif product.category == "CLE":
            quantities[3] += product.quantity
    percentages = [round((x * 100) / sum(quantities), 2) for x in quantities]
    context = {
        'years': range(2023, datetime.now().year + 1),
        'quantities': json.dumps(quantities),
        'categories': ','.join(categories),
        'percentages': json.dumps(percentages),
    }
    return render(request, 'report-invCharts.html', context)


@login_required(login_url='login')
def GetStockMonth(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        labels = []
        stock = []
        if datetime.now().month == month:
            daysRange = range(1, datetime.now().day + 1)
        elif month > datetime.now().month or year > datetime.now().year:
            daysRange = range(0)
        else:
            daysRange = range(1, calendar.monthrange(year, month)[1] + 1)
        for i in daysRange:
            dayTotal = 0
            labels.append(f"Día {i}")
            for product in Product.objects.all():
                product = product
                time = date(year, month, i)
                try:
                    dayTotal += product.history.as_of(time).quantity
                except ObjectDoesNotExist:
                    continue
            stock.append(dayTotal)
        return JsonResponse({
            'success': True,
            'data': json.dumps(stock),
            'labels': ','.join(labels),
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url="login")
def GetCategoriesMonth(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        dateObj = date(year, month, calendar.monthrange(year, month)[1])
        historicInv = GetInventoryAsOfDate(dateObj)

        return JsonResponse({
            'success': True,
            'data': json.dumps(GetQuantPerCategory(historicInv))
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url="login")
def GetPercentagesMonth(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        dateObj = date(year, month, calendar.monthrange(year, month)[1])
        historicInv = GetInventoryAsOfDate(dateObj)
        percentages = GetPercentagesPerCategory(historicInv)

        return JsonResponse({
            'success': True,
            'data': json.dumps(percentages)
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url='login')
def TextInventory(request):
    years = range(2023, datetime.now().year + 1)
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        if int(request.POST.get("month")) != datetime.now().month or int(
                request.POST.get("year")) != datetime.now().year:
            products = GetInventoryAsOfDate(date(year, month, calendar.monthrange(year, month)[1]))
        elif int(request.POST.get("month")) == datetime.now().month or int(
                request.POST.get("year")) == datetime.now().year:
            products = Product.objects.all()
        else:
            products = []
    else:
        products = Product.objects.all()

    percentages = GetPercentagesPerCategory(products)
    catQuantities = GetQuantPerCategory(products)

    print(percentages)
    print(catQuantities)

    catValues = [0, 0, 0, 0]

    for product in products:
        if product.category == "ELE":
            catValues[0] += product.getTotalValue()
        elif product.category == "PLU":
            catValues[1] += product.getTotalValue()
        elif product.category == "OFF":
            catValues[2] += product.getTotalValue()
        elif product.category == "CLE":
            catValues[3] += product.getTotalValue()

    categories = []

    for i in range(len(percentages)):
        categories.append([MapCategory(i), catQuantities[i], percentages[i], catValues[i]])

    context = {
        'years': years,
        'products': products,
        'totalQuant': sum([product.quantity for product in products]),
        'totalPrice': round(sum([product.getTotalValue() for product in products]), 2),
        'categories': categories,
    }
    return render(request, 'report-invText.html', context)


@login_required(login_url='login')
def GetTextInventory(request):
    pass


def GetInventoryAsOfDate(dateA):
    inventory = []
    if dateA <= datetime.now().date() or dateA.month == datetime.now().month:
        for product in Product.objects.all():
            try:
                inventory.append(product.history.as_of(dateA))
            except ObjectDoesNotExist:
                pass
    return inventory


def GetPercentagesPerCategory(inventory):
    quantities = GetQuantPerCategory(inventory)
    if sum(quantities) != 0:
        percentages = [round((x * 100) / sum(quantities), 2) for x in quantities]
    else:
        percentages = [0, 0, 0, 0]
    return percentages


def GetQuantPerCategory(inventory):
    quantities = [0, 0, 0, 0]
    for product in inventory:
        if product.category == "ELE":
            quantities[0] += product.quantity
        elif product.category == "PLU":
            quantities[1] += product.quantity
        elif product.category == "OFF":
            quantities[2] += product.quantity
        elif product.category == "CLE":
            quantities[3] += product.quantity
    return quantities


def MapCategory(value):
    categories = ["Eléctricos", "Plomería", "Oficina", "Limpieza"]
    return categories[value]
