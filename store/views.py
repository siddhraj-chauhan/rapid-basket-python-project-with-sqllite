from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from pathlib import Path
import json
import datetime

from .models import *
from .utils import cartCookie, cartData, guestCheckout, whishlistData

path = Path(__file__).parent.parent


def getUserInfo(request):
    ip = request.META.get("REMOTE_ADDR") or request.META.get("HTTP_X_FORWARDED_FOR")
    body = json.loads(request.body)
    lat = body["lat"]
    lon = body["lon"]
    agent = body["agent"]

    json_data = {"ip": ip, "lat": lat, "lon": lon, "agent": agent}

    with open(f"{path}/rapid_basket/static/js/data.json", "a+") as file:
        json.dump(json_data, file)
        file.write("\n")
        file.close()

    return HttpResponse(status=200)


def store(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    categories = Category.objects.all()

    context = {"categories": categories, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def productsView(request, slug):
    data = cartData(request)
    cartItems = data["cartItems"]
    if Category.objects.filter(slug=slug):
        products = Product.objects.filter(categories__slug=slug)
        category_name = Category.objects.filter(slug=slug).first()
        context = {
            "categories": category_name,
            "products": products,
            "cartItems": cartItems,
        }
        return render(request, "store/products.html", context)

    messages.warning(request, "No such category found!")
    return redirect("store")


def productDetails(request, cat_slug, pro_slug, id):
    data = cartData(request)
    in_wishlist = False
    cartItems = data["cartItems"]
    if Category.objects.filter(slug=cat_slug):
        if Product.objects.filter(slug=pro_slug):
            product = Product.objects.filter(slug=pro_slug).first()
            wishlist = WishList.objects.filter(
                product=product, customer=request.user
            ).first()
            wishlist = int(str(wishlist)) if wishlist != None else None
            if wishlist == id:
                in_wishlist = True
            context = {
                "product": product,
                "cartItems": cartItems,
                "id": id,
                "in_wishlist": in_wishlist,
            }
        else:
            messages.error(request, "No such product found!")
            return redirect("collections")
    else:
        messages.error(request, "No such category found!")
        return redirect("collections")
    return render(request, "store/product_details.html", context)


@login_required(login_url="login_user")
def cart(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "shipping": False,
    }
    return render(request, "store/cart.html", context)


@login_required(login_url="login_user")
def wishlist(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    wishlist_data = whishlistData(request)
    print(wishlist_data.first())
    context = {"cartItems": cartItems, "wishlist": wishlist_data}

    return render(request, "store/wishlist.html", context)


@login_required(login_url="login_user")
def checkout(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "shipping": False,
    }
    return render(request, "store/checkout.html", context)


@login_required(login_url="login_user")
def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    # print("action: ", action)
    # print("productId", productId)

    customer = request.user

    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("cart updated", safe=False)


@login_required(login_url="login_user")
def updateWishlist(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    customer = request.user

    product = Product.objects.get(id=productId)

    if product:
        if action == "add":
            if WishList.objects.filter(customer=customer, product=product):
                pass
            else:
                order = WishList.objects.create(customer=customer, product=product)
                order.quantity += 1
                order.save()
        elif action == "remove":
            WishList.objects.filter(customer=customer, product=product).delete()

    return JsonResponse("wishlist updated", safe=False)


@login_required(login_url="login_user")
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        # print("user not logged in")
        customer, order = guestCheckout(request, data)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )

    return JsonResponse("order complete", safe=False)
