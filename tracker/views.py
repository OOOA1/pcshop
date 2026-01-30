from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView
from django.db.models import Sum

from .models import InventoryItem, Build, BuildItem, Sale, ItemStatus, BuildStatus
from .forms import InventoryItemForm, BuildForm, AddItemToBuildForm, SaleForm


class InventoryListView(ListView):
    model = InventoryItem
    template_name = "tracker/inventory_list.html"
    context_object_name = "items"
    paginate_by = 50

    def get_queryset(self):
        qs = InventoryItem.objects.all().order_by("-created_at")
        status = self.request.GET.get("status") or ""
        category = self.request.GET.get("category") or ""
        q = self.request.GET.get("q") or ""
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category=category)
        if q:
            qs = qs.filter(name__icontains=q)

        # Исключаем проданные и списанные товары из основного списка
        qs = InventoryItem.objects.exclude(
            status__in=[ItemStatus.SOLD, ItemStatus.WRITTEN_OFF]
        ).order_by("-created_at")
        return qs


class InventoryCreateView(CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = "tracker/inventory_form.html"

    def get_success_url(self):
        messages.success(self.request, "Товар добавлен.")
        return reverse("inventory_list")


class InventoryUpdateView(UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = "tracker/inventory_form.html"

    def get_success_url(self):
        messages.success(self.request, "Товар обновлён.")
        return reverse("inventory_list")


class BuildListView(ListView):
    model = Build
    template_name = "tracker/build_list.html"
    context_object_name = "builds"

    def get_queryset(self):
        # Оставляем только те сборки, статус которых НЕ "Продано"
        return Build.objects.exclude(status=BuildStatus.SOLD).order_by("-created_at")


class BuildCreateView(CreateView):
    model = Build
    form_class = BuildForm
    template_name = "tracker/build_form.html"

    def get_success_url(self):
        messages.success(self.request, "Сборка создана.")
        return reverse("build_detail", kwargs={"pk": self.object.pk})


class BuildUpdateView(UpdateView):
    model = Build
    form_class = BuildForm
    template_name = "tracker/build_form.html"

    def get_success_url(self):
        messages.success(self.request, "Сборка обновлена.")
        return reverse("build_detail", kwargs={"pk": self.object.pk})


def build_detail(request, pk: int):
    build = get_object_or_404(Build, pk=pk)
    add_form = AddItemToBuildForm()

    if request.method == "POST" and request.POST.get("action") == "add_item":
        add_form = AddItemToBuildForm(request.POST)
        if add_form.is_valid():
            item = add_form.cleaned_data["item"]
            qty = add_form.cleaned_data["qty"]

            if item.status != ItemStatus.IN_STOCK:
                messages.error(request, "Этот товар уже не на складе.")
                return redirect("build_detail", pk=build.pk)

            BuildItem.objects.create(build=build, item=item, qty=qty)
            item.status = ItemStatus.INSTALLED
            item.save(update_fields=["status"])

            messages.success(request, "Товар добавлен в сборку.")
            return redirect("build_detail", pk=build.pk)

    build_items = build.build_items.select_related("item").all()
    return render(
        request,
        "tracker/build_detail.html",
        {"build": build, "build_items": build_items, "add_form": add_form},
    )


def build_remove_item(request, pk: int, item_id: int):
    build = get_object_or_404(Build, pk=pk)
    bi = get_object_or_404(BuildItem, build=build, item_id=item_id)
    item = bi.item

    bi.delete()

    if item.status in [ItemStatus.INSTALLED, ItemStatus.RESERVED]:
        item.status = ItemStatus.IN_STOCK
        item.save(update_fields=["status"])

    messages.success(request, "Товар убран из сборки и возвращён на склад.")
    return redirect("build_detail", pk=build.pk)

class SaleListView(ListView):
    model = Sale
    template_name = "tracker/sale_list.html"
    context_object_name = "sales"

    def get_queryset(self):
        return Sale.objects.select_related("build").order_by("-sold_at")

    # Добавь этот метод для передачи суммы в шаблон
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Считаем сумму всех проданных сборок
        context['total_revenue'] = self.get_queryset().aggregate(Sum('sold_price'))['sold_price__sum']
        return context


class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "tracker/sale_form.html"

    def form_valid(self, form):
        resp = super().form_valid(form)
        sale = self.object
        build = sale.build

        build.status = BuildStatus.SOLD
        build.save(update_fields=["status"])

        for bi in build.build_items.select_related("item").all():
            it = bi.item
            it.status = ItemStatus.SOLD
            it.save(update_fields=["status"])

        messages.success(self.request, "Продажа записана. Сборка и товары помечены как проданные.")
        return resp

    def get_success_url(self):
        return reverse("sale_list")

class ArchiveView(ListView):
    template_name = "tracker/archive_list.html"
    context_object_name = "sold_builds"

    def get_queryset(self):
            # Добавляем prefetch_related, чтобы подтянуть детали для модалок
            return Build.objects.filter(status=BuildStatus.SOLD).prefetch_related('build_items__item').order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст комплектующие, проданные вне сборок
        context['sold_items'] = InventoryItem.objects.filter(
            status=ItemStatus.SOLD
        ).exclude(build_links__build__status=BuildStatus.SOLD)
        return context

class ArchiveListView(ListView):
    template_name = "tracker/archive_list.html" # Создадим этот шаблон ниже
    context_object_name = "sold_builds"

    def get_queryset(self):
            # Добавляем prefetch_related, чтобы подтянуть детали для модалок
            return Build.objects.filter(status=BuildStatus.SOLD).prefetch_related('build_items__item').order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем отдельно проданные комплектующие (которые не в сборках)
        context['sold_items'] = InventoryItem.objects.filter(
            status=ItemStatus.SOLD
        ).exclude(build_links__build__status=BuildStatus.SOLD)
        return context