from django.urls import path
from . import views

urlpatterns = [
    path("", views.InventoryListView.as_view(), name="inventory_list"),
    path("inventory/add/", views.InventoryCreateView.as_view(), name="inventory_add"),
    path("inventory/<int:pk>/edit/", views.InventoryUpdateView.as_view(), name="inventory_edit"),

    path("builds/", views.BuildListView.as_view(), name="build_list"),
    path("builds/add/", views.BuildCreateView.as_view(), name="build_add"),
    path("builds/<int:pk>/edit/", views.BuildUpdateView.as_view(), name="build_edit"),
    path("builds/<int:pk>/", views.build_detail, name="build_detail"),
    path("builds/<int:pk>/remove/<int:item_id>/", views.build_remove_item, name="build_remove_item"),

    path("sales/", views.SaleListView.as_view(), name="sale_list"),
    path("sales/add/", views.SaleCreateView.as_view(), name="sale_add"),

    path("archive/", views.ArchiveView.as_view(), name="archive_list"),
    path("archive/", views.ArchiveListView.as_view(), name="archive_list"),
]