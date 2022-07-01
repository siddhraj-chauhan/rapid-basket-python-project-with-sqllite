from django.contrib import admin

from .models import *

# Register your models here.
admin.site.site_title = "Rapid Basket"
admin.site.site_header = "Rapid Basket 🛒"
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(WishList)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)