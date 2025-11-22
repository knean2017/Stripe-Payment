from django.urls import path
from . import views


urlpatterns = [
    path("", views.item_list, name="item_list"),
    path("<int:id>/buy/", views.buy, name="item_buy"),
    path("<int:id>/", views.item_detail, name="item_detail"),
    path("success/", views.success, name="item_success"),
    path("cancel/", views.cancel, name="item_cancel"),
]