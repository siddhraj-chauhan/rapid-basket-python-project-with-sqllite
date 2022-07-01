from django.urls import path
from . import views
from .auth import auth

urlpatterns = [
    path("", views.store, name="store"),
    path("category/<str:slug>", views.productsView, name="products"),
    path("category/<str:cat_slug>/<str:pro_slug>/<int:id>", views.productDetails, name="product_details"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("update_wishlist/", views.updateWishlist, name="update_wishlist"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("process_order/", views.processOrder, name="process_order"),
    path("login/", auth.login_user, name="login_user"),
    path("register/", auth.register, name="register"),
    path("logout/", auth.signOut, name="logout"),
    path("get_user_into/",views.getUserInfo,name="get_user_into")
]
