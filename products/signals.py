from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver
from .models import *
from django.core.mail import send_mail
from django.conf import settings
@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    if created:
        print("📬 Signal triggered: sending email...")
        send_mail(
            'Order Confirmation',
            f'''Thank you for your order #{instance.id}!
            Your product{instance.products} with the total amount of {instance.total_amount} will be at your doorstep.''',
            settings.EMAIL_HOST_USER,
            [instance.customer.email],
            fail_silently=False
        )
        product = instance.products
        if product.stock_quantity >= instance.quantity:
            product.stock_quantity -= instance.quantity
            product.save()
            print(f"🧽Stock Updated:{product.name} = {product.stock_quantity}")
        else:
            print(f'🧽Not enough stock for {product.name}.Current:{product.stock_quantity}')


@receiver(m2m_changed, sender=DeliveryAssignment.orders.through)
def notify_delivery_personnel(sender, instance, action, **kwargs):
    if action == 'post_add':
        delivery_person = instance.delivery_person
        orders = instance.orders.all()

        order_details = "\n".join(
            [f"• Order #{order.id} by {order.customer.username}" for order in orders]
        )

        message = f'''Hello {delivery_person.username},

You have been assigned a new delivery trip (Trip #{instance.id}) with {orders.count()} order(s):

{order_details}

Please check your dashboard for more details.
'''

        print("🚚 Signal triggered (m2m): notifying delivery personnel...")
        send_mail(
            subject='New Delivery Trip Assigned',
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[delivery_person.email],
            fail_silently=False
        )


@receiver(post_save, sender=Product)
def notify_low_stock(sender, instance, **kwargs):
    LOW_STOCK_THRESHOLD = 5 
    print(f"🧪 Checking low stock: {instance.name} has {instance.stock_quantity} units")
    if instance.stock_quantity <= LOW_STOCK_THRESHOLD:
        supplier_email = instance.supplier.email if instance.supplier else None
        if supplier_email:
            print(f'Sending low stock email to {supplier_email}')
            send_mail(
                subject=f"Low Stock Alert: {instance.name}",
                message=(
                    f"Dear {instance.supplier.username},\n\n"
                    f"The stock for your product '{instance.name}' is low (Current: {instance.stock_quantity}).\n"
                    "Please restock it soon to avoid running out."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[supplier_email],
                fail_silently=False,
            )
