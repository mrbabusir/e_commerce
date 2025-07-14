from rest_framework import serializers
from .models import *
from users.serializers import *
from django.contrib.auth import get_user_model

User = get_user_model()
        
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.username', read_only = True)

    class Meta:
        model = Product
        fields = ['id', 'supplier_name', 'name', 'description', 'price', 'stock_quantity',
                  'image', 'created_at', 'updated_at', 'category_name']
class CategoryListSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class CategoryDetailSerializer(serializers.ModelSerializer):##made another serializer to see products  in category instance
    products = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products']
    
    def get_products(self, obj):
        products = obj.product_set.all() 
        return ProductSerializer(products, many=True).data


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }

class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'products','quantity', 'shipping_address', 'status', 'payment_status', 'payment_method','total_amount','order_date']
        read_only_fields = ['total_amount', 'status','customer','order_date', 'payment_status']

    def create(self, validated_data): ## total amount calculate gareko
        
        product = validated_data['products']
        quantity = validated_data ['quantity']
        validated_data['total_amount'] = product.price * quantity
        return super().create(validated_data)
    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.role == 'DELIVERY':
            if set(validated_data.keys()) - {'status'}:
                raise serializers.ValidationError("You can only update the order status.")
        return super().update(instance, validated_data)
class OrderStatusSerializer(serializers.ModelSerializer):
    model = Order
    fields = ['id','status']

class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    # delivery_person = serializers.PrimaryKeyRelatedField(source = 'delivery_person.username',read_only=True)
    delivery_person = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='DELIVERY')
    )
    delivery_person_name = serializers.CharField(source='delivery_person.username', read_only=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    class Meta:
        model = DeliveryAssignment
        fields = ['id','delivery_person_name', 'orders', 'status', 'assigned_at']
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request', None)
        user = getattr(request, 'user', None) if request else None
    
        if user and hasattr(user, 'role') and user.role == 'DELIVERY':
            for field_name in fields:
                if field_name != 'status':
                    fields[field_name].read_only = True
        return fields

    # def get_fields(self):
    #     fields = super().get_fields()
    #     user = self.context['request'].user
        
 
    #     # if user.role == 'DELIVERY':
    #     #     for field_name in fields:      ##yedi  user ko role Delivery cha bhane status bhahek baki fields read only rakheko 
    #     #         if field_name != 'status':
    #     #             fields[field_name].read_only = True
    #     # return fields
