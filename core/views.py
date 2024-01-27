from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData
from django.contrib.auth.decorators import login_required


def user(request):
    data = cartData(request)
    cartItems = data["cartItems"]

    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        shipping_address = ShippingAddress.objects.filter(customer=customer).first()
        orders = Order.objects.filter(customer=customer)
        order_items = []

        for order in orders:
            order_item_objects = OrderItem.objects.filter(order=order)
            order_items.append((order, order_item_objects))

        context = {
            "cartItems": cartItems,
            "customer": customer,
            "shipping_address": shipping_address,
            "orders": orders,
            "order_items": order_items,
            "username": request.user.username,
        }
    return render(request, "core/user.html", context)


def index(request):
    data = cartData(request)
    cartItems = data["cartItems"]

    context = {"cartItems": cartItems}
    return render(request, "core/index.html", context)


def store(request):
    data = cartData(request)
    cartItems = data["cartItems"]

    products = Product.objects.all()
    wishlist = Wishlist.objects.get(user=request.user)

    wishlist_product_ids = wishlist.products.values_list("id", flat=True)

    context = {
        "products": products,
        "cartItems": cartItems,
        "wishlist": wishlist,
        "wishlist_product_ids": wishlist_product_ids,
    }
    return render(request, "core/store.html", context)


def category_product_list(request, category_id):
    categoryId = category_id
    data = cartData(request)
    cartItems = data["cartItems"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems, "categoryId": categoryId}
    return render(request, "core/category_product_list.html", context)


def product_detail(request, product_id):
    data = cartData(request)
    cartItems = data["cartItems"]
    product = get_object_or_404(Product, pk=product_id)
    return render(
        request,
        "core/product_detail.html",
        {"product": product, "cartItems": cartItems},
    )


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
    return render(request, "core/cart.html", context)


@login_required
def wishlist(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all()
    return render(
        request,
        "core/wishlist.html",
        {"wishlist": wishlist, "products": products, "cartItems": cartItems},
    )


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.add_to_wishlist(product)
    return redirect("store")


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.remove_from_wishlist(product)
    return redirect("wishlist")


def checkout(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "core/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print("Action", action)
    print("ProdocutId: ", productId)

    customer = request.user.customer
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

    return JsonResponse("item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        print("User is not logged in...")
        print("cookies: ", request.COOKIES)
        name = data["form"]["name"]
        email = data["form"].get("email")
        cookieData = cookieCart(request)
        items = cookieData["items"]
        customer, created = Customer.objects.get_or_create(
            email=email,
        )
        customer.name = name
        customer.save()

        order = Order.objects.create(
            customer=customer,
            complete=False,
        )
        for item in items:
            product = Product.objects.get(id=item["product"]["id"])
            orderItem = OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item["quantity"],
            )
    total = data["form"]["total"]
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

    return JsonResponse("Payment complete", safe=False)


def search_products(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    if request.method == "POST":
        data = cartData(request)
        searched = request.POST["searched"]
        venues = Product.objects.filter(name__contains=searched)
        return render(
            request,
            "core/search.html",
            {"searched": searched, "venues": venues, "cartItems": cartItems},
        )
    else:
        return render(request, "core/search.html", {"cartItems": cartItems})
