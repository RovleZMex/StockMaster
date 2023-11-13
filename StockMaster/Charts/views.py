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
    print(percentages)
    context = {
        'years': range(2023, 2074),
        'quantities': json.dumps(quantities),
        'categories': ','.join(categories),
        'percentages': json.dumps(percentages),
    }
    return render(request, 'report-charts.html', context)


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


def GetInventoryAsOfDate(date):
    inventory = []
    for product in Product.objects.all():
        try:
            inventory.append(product.history.as_of(date))
        except ObjectDoesNotExist:
            print("NAAAAOOO")
    return inventory

def GetPercentagesPerCategory(inventory):
    quantities = GetQuantPerCategory(inventory)
    percentages = [round((x * 100) / sum(quantities), 2) for x in quantities]
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
