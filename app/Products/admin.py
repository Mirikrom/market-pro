from django.contrib import admin
from .models import ProductsList, Unit, UnitConversion, Products, Order, OrderItems


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_base')
    list_filter = ('is_base',)
    search_fields = ('name',)


@admin.register(UnitConversion)
class UnitConversionAdmin(admin.ModelAdmin):
    list_display = ('unit', 'base_unit', 'conversion_factor')
    list_filter = ('unit', 'base_unit')
    search_fields = ('unit__name', 'base_unit__name')


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "base_unit":
             kwargs["queryset"] = Unit.objects.filter(is_base=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(ProductsList)
class ProductsListAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    list_filter = ('unit',)
    search_fields = ('name', 'unit__name')


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('products_list', 'quantity', 'unit', 'purchase_price', 'selling_price', 'created_at')
    list_filter = ('unit',)
    search_fields = ('products_list__name', 'unit__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('ordernumber', 'orderdate', 'orderstatus', 'ordertotalamount', 'orderoperator', 'orderbalance', 'orderclient')
    list_filter = ('orderstatus',)
    search_fields = ('ordernumber', 'orderoperator', 'orderclient')

@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total')
    list_filter = ('order', 'product')
    search_fields = ('order__ordernumber', 'product__name')


