from django.urls import path
from .views import *


urlpatterns = [
    path("", index, name="index"),
    path("profile/", user, name="profile"),
    path("store/", store, name="store"),
    path("cart/", cart, name="cart"),
    path("wishlist/", wishlist, name="wishlist"),
    path("add-to-wishlist/<int:product_id>/", add_to_wishlist, name="add_to_wishlist"),
    path(
        "remove-from-wishlist/<int:product_id>/",
        remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path("checkout/", checkout, name="checkout"),
    path("update_item/", updateItem, name="udpate_item"),
    path("process_order/", processOrder, name="process_order"),
    path("product_detail/<int:product_id>", product_detail, name="product_detail"),
    path(
        "category_products/<int:category_id>/",
        category_product_list,
        name="category_products",
    ),
    path("search/", search_products, name="search"),
]
