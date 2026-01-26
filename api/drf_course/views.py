from django.shortcuts import render
from django.shortcuts import get_list_or_404
from .models import Product,Order,OrderItem
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ProductSerializer,OrderItemSerializer,OrderSerializer,ProductInfoSerializer
from django.db.models import Max

# Create your views here.

@api_view(['GET'])
def product_list(request):
    products=Product.objects.all()
    serializer=ProductSerializer(products,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request,pk):
    product=get_list_or_404(Product,pk=pk)
    serializer=ProductSerializer(product, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def order_list(request):
    orders = Order.objects.prefetch_related('items__product')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def user_order_list_view(request):
    orders = Order.objects.prefetch_related('items__product').filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products': products,
        'count': len(products),
        'max_price': products.aggregate(max_price=Max('price'))['max_price']
    })
    return Response(serializer.data)