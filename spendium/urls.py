from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="spendium-home"),
    path("purchases/", views.purchases_list, name="spendium-purchases-list"),
    path(
        "purchases/<purchase_id>",
        views.purchases_detail,
        name="spendium-purchases-detail",
    ),
]
