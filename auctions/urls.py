from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:item_id>",views.listing_page, name="listing-page"),
    path("close-auction/<int:item_id>", views.close_auction, name="close-auction"),
    path("place-bid/<int:item_id>", views.place_bid, name="place-bid"),
    path("post-comment/<int:item_id>", views.post_comment, name="post-comment"),
    path("add-to-watchlist/<int:item_id>", views.add_to_watchlist, name="add-to-watchlist"),
    path("remove-from-watchlist/<int:item_id>", views.remove_from_watchlist, name="remove-from-watchlist"),
    path("categories", views.categories, name="categories"),
    path("create-listing", views.create_listing, name="create-listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category/<str:category>", views.category, name="category")
]
