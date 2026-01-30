from django import forms
from django.utils import timezone
from .models import InventoryItem, Build, Sale, Consumable, PurchasePlan

# ... (InventoryItemForm и BuildForm оставляем как были) ...

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
        fields = ["title", "category", "status", "description", "listing_url", "cover_image"]
        labels = {
            "title": "Название_сборки",
            "category": "Тип_конфигурации",
            "status": "Статус_проекта",
            "description": "Техническое_задание / Заметки",
            "listing_url": "URL_объявления",
            "cover_image": "Фронтальное_фото",
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono', 'placeholder': 'Например: Gaming Beast i5-12400F'}),
            'category': forms.Select(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono appearance-none'}),
            'status': forms.Select(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono appearance-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono', 'rows': 4}),
            'listing_url': forms.URLInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono'}),
            'cover_image': forms.FileInput(attrs={'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer bg-slate-50 rounded-xl border border-slate-200'}),
        }

class AddItemToBuildForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.filter(status="in_stock"),
        label="Выбор юнита",
        widget=forms.Select(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono appearance-none'})
    )
    qty = forms.IntegerField(
        min_value=1, initial=1, label="QTY",
        widget=forms.NumberInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono', 'placeholder': '1'})
    )

# --- ОБНОВЛЕННАЯ ФОРМА ПРОДАЖИ СБОРКИ ---
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["build", "sold_price", "fees", "sold_at", "notes"]
        labels = {
            "build": "Сборка на продажу",
            "sold_price": "Итоговая цена (₽)",
            "fees": "Налоги и комиссии (₽)",
            "sold_at": "Дата сделки",
            "notes": "Заметки о клиенте",
        }
        widgets = {
            'build': forms.Select(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono appearance-none'}),
            'sold_price': forms.NumberInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono font-bold', 'placeholder': '0.00'}),
            'fees': forms.NumberInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono', 'placeholder': '0.00'}),
            'sold_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono', 'rows': 3, 'placeholder': 'Контакты клиента, условия гарантии...'}),
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
            "name": "Наименование_материала",
            "purchase_price": "Стоимость_закупа",
            "quantity": "Количество",
            "notes": "Заметки_по_кастому",
        }

class AddConsumableToBuildForm(forms.Form):
    consumable = forms.ModelChoiceField(
        queryset=Consumable.objects.filter(quantity__gt=0),
        label="Материал",
        widget=forms.Select(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono appearance-none'})
    )
    qty_used = forms.IntegerField(
        min_value=1, initial=1, label="Кол-во",
        widget=forms.NumberInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono font-bold', 'placeholder': '1'})
    )

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

# --- ОБНОВЛЕННАЯ ФОРМА ПРОДАЖИ ДЕТАЛИ ---
class ItemSaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["sold_price", "fees", "sold_at", "notes"]
        labels = {
            "sold_price": "Цена_продажи (₽)",
            "fees": "Налоги_и_комиссии (₽)",
            "sold_at": "Дата_сделки",
            "notes": "Заметки_о_клиенте",
        }
        widgets = {
            'sold_price': forms.NumberInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono font-bold', 'placeholder': '0.00'}),
            'fees': forms.NumberInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono', 'placeholder': '0.00'}),
            'sold_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'class': 'w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 font-mono', 'rows': 3, 'placeholder': 'Контакты клиента, условия...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['sold_at'].initial = timezone.now()