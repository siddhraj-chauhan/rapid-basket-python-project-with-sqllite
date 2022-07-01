from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from store.form import CreateUserForm
from store.utils import cartData


def register(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, "Account created")
            return redirect("login_user")

    context = {"form": form}

    return render(request, "store/register.html", context)


def login_user(request):

    if request.user.is_authenticated:
        messages.warning(request, "already logged in")
        # data = cartData(request)
        # cartItems = data["cartItems"]
        # order = data["order"]
        # items = data["items"]

        # categories = Category.objects.all()

        # context = {"categories": categories, "cartItems": cartItems}
        # return render(request, "store/store.html", context)
        return redirect("store")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # user = form.cleaned_data.get("username")
        # email = form.cleaned_data.get("email")

        auth_user = authenticate(request, username=username, password=password)

        if auth_user is not None:
            login(request, auth_user)
            return redirect("store")
        else:
            messages.error(request, "invalid username/password")
            return redirect("login_user")

    return render(request, "store/login.html")


def signOut(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "logged out!")
    return redirect("store")

