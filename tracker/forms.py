from django import forms
from django.utils import timezone

from .models import InventoryItem, Build, Sale, ItemStatus, BuildStatus


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ["category", "name", "purchase_price", "status", "serial_number", "notes", "photo"]
        labels = {
            "category": "Категория_детали",
            "name": "Название_модели",
            "purchase_price": "Цена_закупки",
            "status": "Текущий_статус",
            "serial_number": "Серийный_номер (S/N)",
            "notes": "Технические_заметки",
            "photo": "Изображение_юнита",
        }
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

class BuildForm(forms.ModelForm):
    class Meta:
        model = Build
        fields = ["title", "description", "listing_url", "cover_image", "status"]
        labels = {
            "title": "Название_сборки",
            "description": "Техническое_задание",
            "listing_url": "URL_объявления",
            "cover_image": "Фронтальное_фото",
            "status": "Статус_проекта",
        }
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class AddItemToBuildForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.filter(status=ItemStatus.IN_STOCK).order_by("category", "name"),
        label="Товар со склада",
    )
    qty = forms.IntegerField(min_value=1, initial=1, label="Количество")


class SaleForm(forms.ModelForm):
    class Meta:
            model = Sale
            fields = ["build", "sold_price", "fees", "sold_at", "notes"]
            labels = {
                "build": "Выбор_сборки",
                "sold_price": "Итоговая_цена_продажи",
                "fees": "Налоги_и_комиссии",
                "sold_at": "Дата_и_время_сделки",
                "notes": "Комментарий_к_продаже",
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qs = Build.objects.exclude(status=BuildStatus.SOLD).filter(sale__isnull=True).order_by("-created_at")
        self.fields["build"].queryset = qs

        if not self.initial.get("sold_at") and not self.instance.pk:
            self.initial["sold_at"] = timezone.now().strftime("%Y-%m-%dT%H:%M")
