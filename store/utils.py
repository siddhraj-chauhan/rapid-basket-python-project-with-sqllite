import json
from .models import *
from django.contrib.auth.models import User


def cartCookie(request):
    try:
        cart = json.loads(request.COOKIES["cart"])
    except:
        cart = {}
        # print("cart: ", cart)

    items = []
    order = {"get_cart_total": 0, "get_cart_items": 0, "shipping": False}
    cartItems = order["get_cart_items"]

    for i in cart:
        try:
            if cart[i]["quantity"] > 0:
                cartItems += cart[i]["quantity"]

            product = Product.objects.get(id=i)
            total = product.price * cart[i]["quantity"]

            order["get_cart_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            item = {
                "id": product.id,
                "product": {
                    "id": product.id,
                    "name": product.title,
                    "price": product.price,
                    "imageURL": product.imageURL,
                },
                "quantity": cart[i]["quantity"],
                "digital": product.digital,
                "get_total": total,
            }

            items.append(item)

            if product.digital == False:
                order["shipping"] = True
        except:
            pass
    return {"cartItems": cartItems, "order": order, "items": items}


def cartData(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(
            customer=request.user, complete=False
        )
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cartCookie(request)
        cartItems = cookieData["cartItems"]
        order = cookieData["order"]
        items = cookieData["items"]

    return {
        "cartItems": cartItems,
        "order": order,
        "items": items,
    }


def guestCheckout(request, data):
    print("cookie: ", request.COOKIES)
    name = data["form"]["name"]
    email = data["form"]["email"]

    cookieData = cartCookie(request)
    items = cookieData["items"]

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item["product"]["id"])
        oderItem = OrderItem.objects.create(
            product=product, order=order, quantity=item["quantity"]
        )
    return customer, order


def whishlistData(request):
    wishlist_items = WishList.objects.filter(customer=request.user)
    return wishlist_items
