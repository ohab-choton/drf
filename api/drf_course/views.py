from django.shortcuts import render,get_object_or_404
from .models import Product,Order,OrderItem
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .serializers import ProductSerializer,OrderItemSerializer,OrderSerializer,ProductInfoSerializer
from django.db.models import Max,Q
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
 

# Create your views here.

@api_view(['GET','POST'])
def product_list(request):
    if request.method == 'GET':
        query=request.GET.get('query')
        if query == None:
            query=''
        products=Product.objects.filter(Q(name__icontains=query) | Q(price__icontains=query))

        paginator = LimitOffsetPagination()
        paginator.default_limit = 3
        paginated_products = paginator.paginate_queryset(products, request)
        serializer=ProductSerializer(paginated_products,many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
           #admin check
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admin can add product"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def order_list(request):
    orders = Order.objects.prefetch_related('items__product')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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