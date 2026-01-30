from django.urls import path
from . import views

urlpatterns = [
    # ГЛАВНАЯ ТЕПЕРЬ ТУТ
    path("", views.DashboardView.as_view(), name="dashboard"),
    
    path("inventory/", views.InventoryListView.as_view(), name="inventory_list"),
    path("inventory/add/", views.InventoryCreateView.as_view(), name="inventory_add"),
    path("inventory/<int:pk>/edit/", views.InventoryUpdateView.as_view(), name="inventory_edit"),
    
    path("builds/", views.BuildListView.as_view(), name="build_list"),
    path("builds/add/", views.BuildCreateView.as_view(), name="build_add"),
    path("builds/<int:pk>/", views.BuildDetailView.as_view(), name="build_detail"),
    path("builds/<int:build_id>/remove/<int:item_id>/", views.build_remove_item, name="build_remove_item"),
    
    path("sales/", views.SaleListView.as_view(), name="sale_list"),
    path("sales/add/", views.SaleCreateView.as_view(), name="sale_add"),
    
    path("archive/", views.ArchiveView.as_view(), name="archive_list"),
    
    path("consumables/", views.ConsumableListView.as_view(), name="consumable_list"),
    path("consumables/add/", views.ConsumableCreateView.as_view(), name="consumable_add"),

    path("purchases/", views.PurchasePlanListView.as_view(), name="purchase_list"),
    path("purchases/add/", views.PurchasePlanCreateView.as_view(), name="purchase_add"),
    path("purchases/<int:pk>/toggle/", views.purchase_toggle, name="purchase_toggle"),
    path("purchases/<int:pk>/delete/", views.purchase_delete, name="purchase_delete"),
    path('inventory/sell/<int:pk>/', views.ItemSaleCreateView.as_view(), name='inventory_sell'),
]