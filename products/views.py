from .serializers import SupplierSerializer
print(type(SupplierSerializer))  # Should show <class 'type'>
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from users.permissions import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.exceptions import PermissionDenied
# Create your views here.
class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().prefetch_related('product_set')
    pagination_class = Pagination
    filter_backends = [SearchFilter,OrderingFilter]
    search_fields = ['name','description']
    ordering_fields = ['id']
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategoryListSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']: #allowing anyone to see category list
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']: ##only admin can perform actions
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class ProductViewSet(viewsets.ModelViewSet): 
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends =[SearchFilter,OrderingFilter]
    pagination_class = Pagination
    search_fields = ['name','description']
    ordering_fields = ['id']
    def get_queryset(self):
        user = self.request.user        
        if hasattr(user,'role') and user.role == 'SUPPLIER': ##supplier ley login garda he can see only his product
            return Product.objects.filter(supplier=user)
        if not user.is_authenticated:
            return Product.objects.all()
        return Product.objects.all()  #admin and other authenticated users see all products
    def get_permissions(self):
        if self.action in ['list', 'retrieve']: # if permission list or retrienve cha bhane sabai lai allow garney product herna 
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']: 
            permission_classes = [ IsAdmin | IsSupplier] ## if there is give action cha bhane admin or have to supplier
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    def perform_update(self,serializer):
        if self.request.user.role == 'SUPPLIER': ### supplier ley afno product update garney
            product = self.get_object()
            if product.supplier != self.request.user:
                raise PermissionDenied('You can only update your own products')
        serializer.save()

class OrderListViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = Pagination
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAdmin | IsCustomer] #only customer or admin ley matrai order create garna milney
        elif self.action in ['update', 'partial_update']:
            permission_classes = [ IsAdmin | IsOwnerOrAdmin]  ##admin ra customer with an order can update their order
        elif self.action in ['destroy']:
            permission_classes = [IsAuthenticated, IsAdmin] #only admin can destroy
        elif self.action in ['retrieve']:
            permission_classes = [IsAuthenticated, IsAdmin | IsOwnerOrAdmin | IsDeliveryPerson] ##admin , order garney customer ra assign Delivery personnel matra herna milney
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    def get_queryset(self):
        user = self.request.user
        if user.role == 'CUSTOMER':
            return Order.objects.filter(customer=user) ## customer ley aafno order matrai herna milney
        elif user.role == 'DELIVERY':
            return Order.objects.filter(delivery_person=user) ## delivery personnel le afulai assign bhayeko order matrai herna milney
            
        return Order.objects.all()
    def perform_update(self, serializer):
        user = self.request.user
        order = self.get_object()

        if user.role == 'CUSTOMER' and order.customer != user:
            raise PermissionDenied('You can only update your own orders.')

        if user.role == 'DELIVERY' and order.delivery_person != user:
            raise PermissionDenied('You can only update your assigned orders.')

        serializer.save()
class DeliveryTripViewSet(viewsets.ModelViewSet):
    queryset = DeliveryAssignment.objects.all()
    serializer_class = DeliveryAssignmentSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            if self.request.user.role == 'DELIVERY':
                return [IsAuthenticated(), IsDeliveryPerson()]
            return [IsAuthenticated(), IsAdmin()]
        elif self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DELIVERY':
            return DeliveryAssignment.objects.filter(delivery_person=user)
        return super().get_queryset()
