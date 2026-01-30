from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from .models import InventoryItem, Build, BuildItem, Sale, ItemStatus, BuildStatus, Consumable, BuildConsumable, PurchasePlan
from .forms import InventoryItemForm, BuildForm, AddItemToBuildForm, SaleForm, ConsumableForm, AddConsumableToBuildForm, PurchasePlanForm

class InventoryListView(ListView):
    model = InventoryItem
    template_name = "tracker/inventory_list.html"
    context_object_name = "items"
    def get_queryset(self):
        qs = InventoryItem.objects.exclude(status__in=[ItemStatus.SOLD, ItemStatus.WRITTEN_OFF]).order_by("-created_at")
        q = self.request.GET.get("q")
        if q: qs = qs.filter(Q(name__icontains=q) | Q(serial_number__icontains=q))
        status = self.request.GET.get("status")
        if status: qs = qs.filter(status=status)
        return qs

class InventoryCreateView(CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = "tracker/inventory_form.html"
    success_url = reverse_lazy("inventory_list")

    def get_initial(self):
        initial = super().get_initial()
        name = self.request.GET.get('name')
        price = self.request.GET.get('price')
        if name:
            initial['name'] = name
        if price:
            initial['purchase_price'] = price
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        purchase_id = self.request.GET.get('purchase_id')
        if purchase_id:
            PurchasePlan.objects.filter(id=purchase_id).delete()
        return response

class InventoryUpdateView(UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = "tracker/inventory_form.html"
    success_url = reverse_lazy("inventory_list")

class BuildListView(ListView):
    model = Build
    template_name = "tracker/build_list.html"
    context_object_name = "builds"
    
    def get_queryset(self):
        # Показываем ВСЕ сборки (убрали .exclude), новые сверху
        return Build.objects.all().order_by("-created_at")

class BuildCreateView(CreateView):
    model = Build
    form_class = BuildForm
    template_name = "tracker/build_form.html"
    success_url = reverse_lazy("build_list")

class BuildDetailView(DetailView):
    model = Build
    template_name = "tracker/build_detail.html"
    context_object_name = "build"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["build_items"] = self.object.build_items.select_related("item")
        context["custom_materials"] = self.object.custom_materials.select_related("consumable")
        context["add_form"] = AddItemToBuildForm()
        context["custom_form"] = AddConsumableToBuildForm()
        return context

    def post(self, request, *args, **kwargs):
        build = self.get_object()
        action = request.POST.get("action")
        
        if action == "add_item":
            form = AddItemToBuildForm(request.POST)
            if form.is_valid():
                item = form.cleaned_data["item"]
                qty = form.cleaned_data["qty"]
                BuildItem.objects.create(build=build, item=item, qty=qty)
                item.status = ItemStatus.INSTALLED
                item.save()
        
        elif action == "add_custom":
            form = AddConsumableToBuildForm(request.POST)
            if form.is_valid():
                consumable = form.cleaned_data["consumable"]
                qty = form.cleaned_data["qty_used"]
                BuildConsumable.objects.create(build=build, consumable=consumable, qty_used=qty)
                # Уменьшаем остаток
                consumable.quantity -= qty
                consumable.save()

        # --- НОВАЯ ЛОГИКА: Обновление часов ---
        elif action == "update_hours":
            hours = request.POST.get("work_hours")
            if hours:
                build.work_hours = hours
                build.save()
        # --------------------------------------
                
        return redirect("build_detail", pk=build.pk)

def build_remove_item(request, build_id, item_id):
    build_item = get_object_or_404(BuildItem, build_id=build_id, item_id=item_id)
    item = build_item.item
    item.status = ItemStatus.IN_STOCK
    item.save()
    build_item.delete()
    return redirect("build_detail", pk=build_id)

class SaleListView(ListView):
    model = Sale
    template_name = "tracker/sale_list.html"
    context_object_name = "sales"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_revenue'] = self.get_queryset().aggregate(Sum('sold_price'))['sold_price__sum']
        return context

class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "tracker/sale_form.html"
    success_url = reverse_lazy("sale_list")

class ArchiveView(ListView):
    template_name = "tracker/archive_list.html"
    context_object_name = "sold_builds"
    def get_queryset(self):
        return Build.objects.filter(status=BuildStatus.SOLD).prefetch_related('build_items__item').order_by("-created_at")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sold_items'] = InventoryItem.objects.filter(status=ItemStatus.SOLD).exclude(build_links__build__status=BuildStatus.SOLD)
        return context

class ConsumableListView(ListView):
    model = Consumable
    template_name = "tracker/consumable_list.html"
    context_object_name = "consumables"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_spent'] = Consumable.objects.aggregate(Sum('purchase_price'))['purchase_price__sum']
        return context

class ConsumableCreateView(CreateView):
    model = Consumable
    form_class = ConsumableForm
    template_name = "tracker/consumable_form.html"
    success_url = reverse_lazy('consumable_list')

class PurchasePlanListView(ListView):
    model = PurchasePlan
    template_name = "tracker/purchase_list.html"
    context_object_name = "plans"
    def get_queryset(self):
        return PurchasePlan.objects.all().order_by("is_bought", "-created_at")

class PurchasePlanCreateView(CreateView):
    model = PurchasePlan
    form_class = PurchasePlanForm
    template_name = "tracker/purchase_form.html"
    success_url = reverse_lazy("purchase_list")

def purchase_toggle(request, pk):
    plan = get_object_or_404(PurchasePlan, pk=pk)
    plan.is_bought = not plan.is_bought
    plan.save()
    return redirect("purchase_list")

def purchase_delete(request, pk):
    plan = get_object_or_404(PurchasePlan, pk=pk)
    plan.delete()
    return redirect("purchase_list")

class DashboardView(ListView):
    template_name = "tracker/dashboard.html"
    context_object_name = "latest_sales"

    def get_queryset(self):
        return Sale.objects.select_related('build').order_by('-sold_at')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Основные KPI
        all_sales = Sale.objects.select_related('build').all()
        context['total_profit'] = sum(s.profit for s in all_sales)
        context['total_revenue'] = all_sales.aggregate(Sum('sold_price'))['sold_price__sum'] or 0
        context['inventory_value'] = InventoryItem.objects.filter(status='in_stock').aggregate(Sum('purchase_price'))['purchase_price__sum'] or 0
        
        # 2. График динамики (общий профит по последним продажам)
        sales_for_chart = Sale.objects.order_by('-sold_at')[:7]
        context['chart_labels'] = [s.build.title for s in sales_for_chart][::-1]
        context['chart_data'] = [float(s.profit) for s in sales_for_chart][::-1]
        
        # 3. АНАЛИТИКА ПО КАТЕГОРИЯМ (Новое)
        # Собираем словарь: {'Игровая': {'count': 5, 'profit': 50000}, ...}
        cat_stats = {}
        for sale in all_sales:
            cat_name = sale.build.get_category_display() # Получаем "Игровая", а не "gaming"
            if cat_name not in cat_stats:
                cat_stats[cat_name] = {'count': 0, 'profit': 0}
            
            cat_stats[cat_name]['count'] += 1
            cat_stats[cat_name]['profit'] += float(sale.profit)
            
        # Разбираем словарь на списки для Chart.js
        context['cat_labels'] = list(cat_stats.keys())
        context['cat_counts'] = [data['count'] for data in cat_stats.values()]
        context['cat_profits'] = [data['profit'] for data in cat_stats.values()]
        
        return context