from django import forms
from .models import InventoryItem, Build, BuildItem, Sale, Consumable, BuildConsumable, PurchasePlan
from django.utils import timezone

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

class AddItemToBuildForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.filter(status="in_stock"),
        label="Выбор_юнита"
    )
    qty = forms.IntegerField(min_value=1, initial=1, label="QTY")

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
        widgets = {
            'sold_at': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'w-full p-3 rounded-xl bg-slate-50 border-none font-mono text-sm'
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только те сборки, которые еще не проданы
        self.fields['build'].queryset = Build.objects.exclude(status="sold")
        
        # АВТО-ДАТА: Если форма пустая (создание), ставим текущее время
        if not self.instance.pk:
            self.fields['sold_at'].initial = timezone.now()

class ConsumableForm(forms.ModelForm):
    class Meta:
        model = Consumable
        fields = ["name", "purchase_price", "quantity", "notes"]
        labels = {
            "name": "Наименование_материала",
            "purchase_price": "Стоимость_закупа",
            "quantity": "Количество",
            "notes": "Заметки_по_кастому",
        }

class AddConsumableToBuildForm(forms.Form):
    consumable = forms.ModelChoiceField(
        queryset=Consumable.objects.filter(quantity__gt=0),
        label="Материал"
    )
    qty_used = forms.IntegerField(min_value=1, initial=1, label="Кол-во")

class PurchasePlanForm(forms.ModelForm):
    class Meta:
        model = PurchasePlan
        fields = ["item_name", "expected_price", "is_bought", "notes"]
        labels = {
            "item_name": "Что нужно купить",
            "expected_price": "Ожидаемая цена",
            "is_bought": "Куплено",
            "notes": "Заметки",
        }