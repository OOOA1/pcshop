from django.db import models
from django.core.validators import MinValueValidator


class ItemStatus(models.TextChoices):
    IN_STOCK = "in_stock", "На складе"
    RESERVED = "reserved", "Зарезервирован"
    INSTALLED = "installed", "В сборке"
    SOLD = "sold", "Продан"
    WRITTEN_OFF = "written_off", "Списан"


class BuildStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    PUBLISHED = "published", "Опубликован"
    SOLD = "sold", "Продан"
    CANCELLED = "cancelled", "Отменён"


class Category(models.TextChoices):
    CPU = "cpu", "CPU"
    GPU = "gpu", "GPU"
    MB = "mb", "Motherboard"
    RAM = "ram", "RAM"
    SSD = "ssd", "SSD"
    HDD = "hdd", "HDD"
    PSU = "psu", "PSU"
    CASE = "case", "Case"
    COOLER = "cooler", "Cooler"
    OTHER = "other", "Other"


class InventoryItem(models.Model):
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    name = models.CharField(max_length=200)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=ItemStatus.choices, default=ItemStatus.IN_STOCK)
    serial_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to="items/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Build(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    listing_url = models.URLField(blank=True)
    cover_image = models.ImageField(upload_to="builds/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=BuildStatus.choices, default=BuildStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    items = models.ManyToManyField(InventoryItem, through="BuildItem", related_name="builds")

    def __str__(self):
        return self.title

    @property
    def cost(self):
        total = 0
        for bi in self.build_items.select_related("item").all():
            total += float(bi.item.purchase_price) * bi.qty
        return total


class BuildItem(models.Model):
    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name="build_items")
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name="build_links")
    qty = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [("build", "item")]

    def __str__(self):
        return f"{self.build} -> {self.item} x{self.qty}"


class Sale(models.Model):
    build = models.OneToOneField(Build, on_delete=models.PROTECT, related_name="sale")
    sold_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    fees = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    sold_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Продажа: {self.build} за {self.sold_price}"

    @property
    def profit(self):
        return float(self.sold_price) - float(self.fees) - float(self.build.cost)
