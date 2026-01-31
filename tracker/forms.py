from django import forms
from django.utils import timezone
from .models import InventoryItem, Build, Sale, Consumable, PurchasePlan

# --- СТИЛИ ДЛЯ ВСЕХ ФОРМ (Общий набор классов) ---
# Чтобы везде было одинаково красиво
INPUT_CLASSES = 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono'
SELECT_CLASSES = 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono appearance-none'
CHECKBOX_CLASSES = 'w-5 h-5 text-indigo-600 bg-slate-100 border-slate-300 rounded focus:ring-indigo-500 focus:ring-2'
FILE_CLASSES = 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer bg-slate-50 rounded-xl border border-slate-200'

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ["category", "name", "purchase_price", "status", "serial_number", "notes", "photo"]
        labels = {
            "category": "Категория детали",
            "name": "Название модели",
            "purchase_price": "Цена закупки (₽)",
            "status": "Текущий статус",
            "serial_number": "Серийный номер (S/N)",
            "notes": "Технические заметки",
            "photo": "Фотография",
        }
        widgets = {
            'category': forms.Select(attrs={'class': SELECT_CLASSES}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Например: RX 580'}),
            'purchase_price': forms.NumberInput(attrs={'class': INPUT_CLASSES + ' font-bold', 'placeholder': '0.00'}),
            'status': forms.Select(attrs={'class': SELECT_CLASSES}),
            'serial_number': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'S/N...'}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': FILE_CLASSES}),
        }

class BuildForm(forms.ModelForm):
    class Meta:
        model = Build
        fields = ["title", "category", "status", "description", "listing_url", "cover_image"]
        labels = {
            "title": "Название сборки",
            "category": "Тип конфигурации",
            "status": "Статус проекта",
            "description": "Описание / Характеристики",
            "listing_url": "Ссылка на объявление",
            "cover_image": "Главное фото",
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Например: Фаррух PC'}),
            'category': forms.Select(attrs={'class': SELECT_CLASSES}),
            'status': forms.Select(attrs={'class': SELECT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 4}),
            'listing_url': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'cover_image': forms.FileInput(attrs={'class': FILE_CLASSES}),
        }

class AddItemToBuildForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.filter(status="in_stock"),
        label="Добавить деталь со склада",
        widget=forms.Select(attrs={'class': SELECT_CLASSES})
    )
    qty = forms.IntegerField(
        min_value=1, initial=1, label="Кол-во",
        widget=forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': '1'})
    )

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["build", "sold_price", "fees_percentage", "fees", "sold_at", "notes"]
        labels = {
            "build": "Сборка на продажу",
            "sold_price": "Итоговая цена (₽)",
            "fees_percentage": "Комиссия сервиса (%)",
            "fees": "Комиссия в рублях (авто)",
            "sold_at": "Дата и время сделки",
            "notes": "Заметки о клиенте",
        }
        widgets = {
            'build': forms.Select(attrs={'class': SELECT_CLASSES}),
            'sold_price': forms.NumberInput(attrs={'class': INPUT_CLASSES + ' font-bold', 'placeholder': '0.00'}),
            'fees_percentage': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Например: 228'}),
            'fees': forms.NumberInput(attrs={'class': INPUT_CLASSES.replace('bg-slate-50', 'bg-slate-100 text-slate-500'), 'placeholder': '0.00'}),
            'sold_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': INPUT_CLASSES}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 3, 'placeholder': 'Контакты, гарантия...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['build'].queryset = Build.objects.exclude(status="sold")
        if not self.instance.pk:
            self.fields['sold_at'].initial = timezone.now()

class ConsumableForm(forms.ModelForm):
    class Meta:
        model = Consumable
        fields = ["name", "purchase_price", "quantity", "notes"]
        labels = {
            "name": "Наименование материала",
            "purchase_price": "Стоимость закупа",
            "quantity": "Количество",
            "notes": "Заметки",
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Например: Краска Kudo'}),
            'purchase_price': forms.NumberInput(attrs={'class': INPUT_CLASSES + ' font-bold', 'placeholder': '0.00'}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': '1'}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 3}),
        }

class AddConsumableToBuildForm(forms.Form):
    consumable = forms.ModelChoiceField(
        queryset=Consumable.objects.filter(quantity__gt=0),
        label="Расходный материал",
        # Теперь тоже светлый стиль для единообразия
        widget=forms.Select(attrs={'class': SELECT_CLASSES})
    )
    qty_used = forms.IntegerField(
        min_value=1, initial=1, label="Расход",
        widget=forms.NumberInput(attrs={'class': INPUT_CLASSES + ' font-bold', 'placeholder': '1'})
    )

class PurchasePlanForm(forms.ModelForm):
    class Meta:
        model = PurchasePlan
        fields = ["item_name", "expected_price", "is_bought", "notes"]
        labels = {
            "item_name": "Что нужно купить",
            "expected_price": "План. цена",
            "is_bought": "Уже куплено?",
            "notes": "Заметки / Ссылка",
        }
        widgets = {
            'item_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Например: БП от Светланы'}),
            'expected_price': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': '0.00'}),
            'is_bought': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 2}),
        }

class ItemSaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["sold_price", "fees_percentage", "fees", "sold_at", "notes"]
        labels = {
            "sold_price": "Цена продажи (₽)",
            "fees_percentage": "Комиссия сервиса (%)",
            "fees": "Комиссия в рублях (авто)",
            "sold_at": "Дата сделки",
            "notes": "Заметки о клиенте",
        }
        widgets = {
            'sold_price': forms.NumberInput(attrs={'class': INPUT_CLASSES + ' font-bold', 'placeholder': '0.00'}),
            'fees_percentage': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Например: 5'}),
            'fees': forms.NumberInput(attrs={'class': INPUT_CLASSES.replace('bg-slate-50', 'bg-slate-100 text-slate-500'), 'placeholder': '0.00'}),
            'sold_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': INPUT_CLASSES}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['sold_at'].initial = timezone.now()