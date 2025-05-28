# from decimal import Decimal
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.db.models import F
# from .models import Products, UnitConversion
#
# @receiver(post_save, sender=Products)
# def update_total_weight_and_quantity(sender, instance, created, **kwargs):
#     # Signal o'zini o'zi qayta chaqirmasligi uchun triggerni oldini olish
#     if 'total_weight' in kwargs.get('update_fields', []):
#         return  # Agar `total_weight` allaqachon yangilangan bo‘lsa, signalni to‘xtatamiz
#
#     # Mahsulotning birligi va asosiy birligini aniqlash
#     unit = instance.unit
#     product_list = instance.name
#     unit_base = product_list.unit  # Mahsulotning asosiy birligi
#
#     # 1. Agar unit asosiy birlikka teng bo‘lsa
#     if unit == unit_base:
#         total_weight = Decimal(instance.quantity)
#
#     # 2. Agar unit asosiy birlikka teng bo‘lmasa
#     else:
#         conversion = UnitConversion.objects.filter(unit=unit, base_unit=unit_base).first()
#
#         if conversion:
#             total_weight = Decimal(instance.quantity) * Decimal(conversion.conversion_factor)
#         else:
#             total_weight = Decimal(0)
#
#     # Yangi total_weightni saqlash
#     if instance.total_weight != total_weight:
#         instance.total_weight = total_weight
#         instance.save(update_fields=['total_weight'])  # Faqat kerakli maydonni yangilash uchun
#
#     # ProductsList jadvalidagi umumiy miqdorni yangilash
#     product_list.total_quantity = F('total_quantity') + total_weight
#     product_list.save(update_fields=['total_quantity'])
