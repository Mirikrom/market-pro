from django.db import models
from django.utils.timezone import now

class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_base = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'unit'
        verbose_name = 'Birlik'
        verbose_name_plural = 'Birliklar'


class UnitConversion(models.Model):
    unit = models.ForeignKey(Unit, related_name='conversions', on_delete=models.CASCADE)
    base_unit = models.ForeignKey(Unit, related_name='base_conversions', on_delete=models.CASCADE)
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"{self.unit.name} -> {self.base_unit.name} ({self.conversion_factor})"

    class Meta:
        db_table = 'unit_conversion'
        verbose_name = 'Birlik konversiyasi'
        verbose_name_plural = 'Birlik konversiyalari'


class ProductsList(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        limit_choices_to={'is_base': True},
        related_name='products'
    )
    total_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Umumiy miqdor"
    )  # Umumiy miqdorni saqlash uchun
    latest_selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Oxirgi sotilish narxi"
    )  # Oxirgi sotilish narxini saqlash uchun

    def __str__(self):
        #need return id
        return self.name

    class Meta:
        db_table = 'products_list'
        verbose_name = 'Mahsulot ro\'yhati'
        verbose_name_plural = 'Mahsulotlar ro\'yhati'


class Products(models.Model):
    products_list = models.ForeignKey('ProductsList', on_delete=models.CASCADE, related_name='product_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='product_units')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Umumiy og'irlik"
    )
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.products_list)

    class Meta:
        db_table = 'products'
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'

#Need translation log order id, order date, order status, order total amount, order operator, order balance, order client
class Order(models.Model):
    ordernumber = models.CharField(max_length=100)
    orderdate = models.DateTimeField(auto_now_add=True)
    orderstatus = models.CharField(max_length=100)
    ordertotalamount = models.DecimalField(max_digits=10, decimal_places=2)
    orderoperator = models.CharField(max_length=100, default="admin")
    orderbalance = models.DecimalField(max_digits=10, decimal_places=2)
    orderclient = models.CharField(max_length=100, default="Guest")

    def __str__(self):
        return self.ordernumber

    class Meta:
        db_table = 'order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class OrderItems(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('ProductsList', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'    