from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from spendium.models import Purchase


def home(request):
    return render(request, "spendium/home.html", locals())


@login_required
def purchases_list(request):
    transactions = Purchase.objects.filter(user=request.user).order_by("-timestamp")[
        :50
    ]
    return render(request, "spendium/purchases_list.html", locals())


@login_required
def purchases_detail(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    return render(request, "spendium/purchases_detail.html", locals())
