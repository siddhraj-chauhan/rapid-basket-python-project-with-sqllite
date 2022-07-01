from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.CharField(blank=True, null=True, max_length=150)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ""
        return url

    @property
    def get_products(self):
        return Product.objects.filter(categories=self.title)


class Product(models.Model):
    title = models.CharField(max_length=200)
    small_desc = models.CharField(
        max_length=100,
        null=False,
    )
    desc = models.CharField(max_length=300)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=True)
    pro_image = models.ImageField(null=True, blank=True)
    categories = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE)
    slug = models.CharField(blank=True, null=True, max_length=150)

    def __str__(self):
        return self.title

    @property
    def imageURL(self):
        try:
            url = self.pro_image.url
        except:
            url = ""
        return url

    @property
    def get_wishlist_total(self):
        wishlist = self.wishlist_set.all().first()
        wishlist = str(wishlist) if wishlist != None else None
        if wishlist != None:
            total = sum([int(item) for item in wishlist])
        else:
            total = 0
        print("total: ",total)
        return total


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class WishList(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return str(self.product.id)
