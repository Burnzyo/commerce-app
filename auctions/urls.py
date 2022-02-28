from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.createListing, name="create"),
    path("auction/<int:auctionId>", views.getAuction, name="auction"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("closed/<int:auctionId>", views.closeAuction, name="closeAuction"),
    path("closed", views.closed, name="closed"),
    path("categories/<str:category>", views.categories, name="category"),
    path("categories", views.listCategories, name="listCategories")
]
