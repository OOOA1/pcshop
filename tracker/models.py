from django.db import models

class ItemStatus(models.TextChoices):
    IN_STOCK = "in_stock", "На складе"
    INSTALLED = "installed", "В сборке"
    SOLD = "sold", "Продан"
    WRITTEN_OFF = "written_off", "Списан"

class Category(models.TextChoices):
    CPU = "cpu", "Процессор"
    GPU = "gpu", "Видеокарта"
    MOTHERBOARD = "motherboard", "Материнская плата"
    RAM = "ram", "Оперативная память"
    SSD = "ssd", "SSD накопитель"
    HDD = "hdd", "Жесткий диск"
    PSU = "psu", "Блок питания"
    CASE = "case", "Корпус"
    COOLER = "cooler", "Охлаждение"
    OTHER = "other", "Прочее"

class BuildStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    PUBLISHED = "published", "Выставлен на продажу"
    SOLD = "sold", "Продан"

# --- НОВАЯ КЛАССИФИКАЦИЯ ---
class BuildCategory(models.TextChoices):
    GAMING = "gaming", "Игровая"
    OFFICE = "office", "Офисная"
    WORKSTATION = "workstation", "Рабочая станция"
# ---------------------------

class InventoryItem(models.Model):
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.OTHER)
    name = models.CharField(max_length=200)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ItemStatus.choices, default=ItemStatus.IN_STOCK)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="items/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()}: {self.name}"

class Build(models.Model):
    title = models.CharField(max_length=200)
    
    # --- НОВОЕ ПОЛЕ: КАТЕГОРИЯ ---
    category = models.CharField(
        max_length=20, 
        choices=BuildCategory.choices, 
        default=BuildCategory.GAMING, 
        verbose_name="Тип сборки"
    )
    # -----------------------------
    
    description = models.TextField(blank=True, null=True)
    listing_url = models.URLField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="builds/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=BuildStatus.choices, default=BuildStatus.DRAFT)
    
    # Поле учета времени
    work_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name="Затрачено часов")
    
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def cost(self):
        hardware_cost = sum(link.item.purchase_price * link.qty for link in self.build_items.all())
        custom_cost = sum(link.consumable.purchase_price * link.qty_used for link in self.custom_materials.all())
        return hardware_cost + custom_cost

    def __str__(self):
        return self.title

class BuildItem(models.Model):
    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name="build_items")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="build_links")
    qty = models.PositiveIntegerField(default=1)

class Sale(models.Model):
    # Теперь ссылка на сборку может быть пустой
    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name="sale_record", null=True, blank=True)
    
    # Ссылка на деталь (для продажи по частям)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="sale_record", null=True, blank=True)
    
    sold_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена продажи")
    
    # --- НОВОЕ ПОЛЕ: Комиссия в процентах ---
    fees_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Комиссия %")
    # ----------------------------------------

    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Комиссия (руб)")
    sold_at = models.DateTimeField(verbose_name="Дата продажи")
    notes = models.TextField(blank=True, null=True, verbose_name="Заметки")

    @property
    def profit(self):
        # Если продана сборка
        if self.build:
            return self.sold_price - self.fees - self.build.cost
        # Если продана деталь
        elif self.item:
            return self.sold_price - self.fees - self.item.purchase_price
        return 0

    def save(self, *args, **kwargs):
        # АВТОМАТИЧЕСКИЙ РАСЧЕТ КОМИССИИ
        # Если указан процент больше 0, пересчитываем поле fees (в рублях)
        if self.fees_percentage is not None and self.fees_percentage > 0:
            self.fees = self.sold_price * (self.fees_percentage / 100)
            
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Логика для сборки: меняем статус на SOLD
            if self.build:
                self.build.status = BuildStatus.SOLD
                self.build.save()
                for bi in self.build.build_items.all():
                    bi.item.status = ItemStatus.SOLD
                    bi.item.save()
            
            # Логика для отдельной детали: меняем статус на SOLD
            elif self.item:
                self.item.status = ItemStatus.SOLD
                self.item.save()

class Consumable(models.Model):
    name = models.CharField(max_length=200)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    purchased_at = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class BuildConsumable(models.Model):
    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name="custom_materials")
    consumable = models.ForeignKey(Consumable, on_delete=models.CASCADE)
    qty_used = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.consumable.name} для {self.build.title}"

class PurchasePlan(models.Model):
    item_name = models.CharField(max_length=200)
    expected_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_bought = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name

