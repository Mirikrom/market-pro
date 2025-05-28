import sys

from django.contrib import messages
from django.db.models import Min, Max, Sum, F, Q, Subquery
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.urls import reverse
import decimal
from django.core.serializers import serialize
import json
from .models import Products, Unit, ProductsList, UnitConversion
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItems
from django.utils import timezone
from django.utils.timezone import now




def index(request):
    products = ProductsList.objects.all()
    # Mahsulotlarni JSON formatga o'tkazamiz
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'latest_selling_price': float(product.latest_selling_price) if product.latest_selling_price is not None else 0.0,
            'total_quantity': float(product.total_quantity) if product.total_quantity is not None else 0.0
        })
    
    # JSON ma'lumotlarni template kontekstiga qo'shamiz
    context = {
        'products': json.dumps(products_data)
    }
    
    return render(request, 'index.html', context)




def add_product(request, product_id=None):   
    print("Hello1")   
    products = ProductsList.objects.all()
    units = Unit.objects.all()
    units_is_base = Unit.objects.filter(is_base=True)
    selected_product_id = product_id or request.GET.get('product_id')
    
    # URL ni shakllantirish
    add_product_url = reverse('add_product_with_id', kwargs={'product_id': selected_product_id}) if selected_product_id else "add_product"
    
    # Birliklarni filtrlash
    if selected_product_id:
        product = ProductsList.objects.get(id=selected_product_id)
        unit = product.unit_id
        units = Unit.objects.filter(
            Q(id=unit) | 
            Q(id__in=UnitConversion.objects.filter(base_unit_id=unit).values("unit_id"))
        ).order_by("id")

    data = {
        'selected_product_id': selected_product_id,
        'products': products,
        'units': units,
        'units_is_base': units_is_base,
        'add_product_url': add_product_url
    }

    if request.method == 'POST':
        if 'new_product_name' in request.POST:
            return handle_new_product(request)
        else:
            return handle_existing_product(request, selected_product_id)
            
    return render(request, 'add_product.html', data)

def handle_new_product(request):
    """Yangi mahsulot qo'shish"""
    try:
        new_product = ProductsList.objects.create(
            name=request.POST.get('new_product_name'),
            unit_id=request.POST.get('base_unit')
        )
        messages.success(request, 'Mahsulot nomi muvaffaqiyatli qo\'shildi!')
        return redirect('add_product')
    except IntegrityError:
        messages.error(request, 'Mahsulot nomi allaqachon mavjud!')
    except Exception as e:
        messages.error(request, f'Xatolik yuz berdi: {str(e)}')
    return redirect('add_product')

def handle_existing_product(request, product_id):
    """Mavjud mahsulotga yangi ma'lumot qo'shish"""
    try: 
        product_name = ProductsList.objects.get(id=product_id)
        quantity = request.POST.get('quantity')
        unit = Unit.objects.get(id=request.POST.get('unit'))
        purchase_price = request.POST.get('purchase_price')
        selling_price = request.POST.get('selling_price')
        if all([product_name, quantity, unit, purchase_price, selling_price]):
            new_product = Products.objects.create(
                products_list=product_name,
                quantity=quantity,
                unit=unit,
                purchase_price=purchase_price,
                selling_price=selling_price
            )
            if unit.is_base:
                converted_quantity = decimal.Decimal(quantity)
            else:
                conversion = UnitConversion.objects.get(
                    unit=unit,
                    base_unit=product_name.unit
                )
                converted_quantity = decimal.Decimal(quantity) * conversion.conversion_factor

            product_name.total_quantity = F('total_quantity') + converted_quantity
            product_name.latest_selling_price = selling_price
            product_name.save(update_fields=['total_quantity', 'latest_selling_price'])

            messages.success(request, 'Mahsulot muvaffaqiyatli qo\'shildi!')
            return redirect('add_product')
        else:
            messages.error(request, 'Iltimos, barcha maydonlarni to\'ldiring.')
    except IntegrityError:
        messages.error(request, 'Mahsulot nomi allaqachon mavjud!')
    except Exception as e:
        messages.error(request, f'Xatolik yuz berdi: {str(e)}')
    return redirect('add_product')



def add_unit(request):
    if request.method == 'POST':
        name = request.POST.get('new_unit_name')
        # base_unit_id = request.POST.get('base_unit')

        if not name:
            messages.error(request, "Hamma maydonlar to'ldirilishi shart.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # 1. Unit qo‘shamiz (agar yo‘q bo‘lsa)
        unit, created = Unit.objects.get_or_create(
            name=name,
            defaults={'is_base': True}
        )

    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
# @csrf_exempt  # faqat testda, prod uchun fetchdan csrf yuboring
def process_sale(request):
    try:
        data = json.loads(request.body)
        cart = data.get("products", [])


        if not cart:
            return JsonResponse({"success": False, "message": "Savat bo‘sh!"}, status=400)

        with transaction.atomic():
            total_sum = Decimal("0.00")

            # ✅ 1. Order yaratamiz
            order = Order.objects.create(
                ordernumber=f"ORD-{int(now().timestamp())}",
                orderdate=now(),
                orderstatus="completed",
                ordertotalamount=0,
                orderbalance=0,
            )

            # ✅ 2. Har bir mahsulot uchun OrderItems yozamiz va zaxiradan ayiramiz
            for item in cart:
                product_id = item.get("id")
                requested_qty = Decimal(item.get("quantity", 0))
                price = Decimal(item.get("price", 0))

                try:
                    product = ProductsList.objects.select_for_update().get(id=product_id)
                except ProductsList.DoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "message": f"ID {product_id} bilan mahsulot topilmadi"
                    }, status=404)

                if product.total_quantity < requested_qty:
                    return JsonResponse({
                        "success": False,
                        "message": f"{product.name} dan faqat {product.total_quantity} dona mavjud, {requested_qty} so‘raldi"
                    }, status=400)

                # Zaxiradan ayiramiz
                product.total_quantity -= requested_qty
                product.save(update_fields=['total_quantity'])

                # Chekga mahsulot qo‘shamiz
                OrderItems.objects.create(
                    order=order,
                    product=product,
                    quantity=requested_qty,
                    price=price,
                    total=price * requested_qty
                )

                total_sum += price * requested_qty

            # ✅ 3. Chekka umumiy summani yozamiz
            order.ordertotalamount = total_sum
            order.save()

        return JsonResponse({"success": True, "message": "✅ Sotuv amalga oshirildi", "order_id": order.id})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "JSON formatida xatolik"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Server xatosi: {str(e)}"}, status=500)


def order_list(request):
    orders = Order.objects.all().order_by('-orderdate')
    return render(request, 'order_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItems.objects.filter(order=order)
    return render(request, 'order_detail.html', {'order': order, 'items': items})

