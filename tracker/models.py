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
    description = models.TextField(blank=True, null=True)
    listing_url = models.URLField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="builds/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=BuildStatus.choices, default=BuildStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    work_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name="Затрачено часов")

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
    build = models.OneToOneField(Build, on_delete=models.CASCADE, related_name="sale_record")
    sold_price = models.DecimalField(max_digits=10, decimal_places=2)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sold_at = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    @property
    def profit(self):
        return self.sold_price - self.fees - self.build.cost

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.build.status = BuildStatus.SOLD
            self.build.save()
            for bi in self.build.build_items.all():
                bi.item.status = ItemStatus.SOLD
                bi.item.save()

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