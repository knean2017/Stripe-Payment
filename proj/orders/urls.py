# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_order, name="create_order"),
    path("add/", views.add_to_order, name="add_to_order"),
    path("<int:id>/", views.order_detail, name="order_detail"),
    path("<int:id>/buy/", views.buy_order, name="buy_order"),
    path("<int:id>/success/", views.order_success, name="order_success"),
    path("<int:id>/cancel/", views.order_cancel, name="order_cancel"),
    path("", views.order_list, name="order_list"),
]