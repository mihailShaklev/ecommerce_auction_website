from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
from datetime import datetime


def index(request):
    listings = Listings.objects.all()
    return render(request, "auctions/index.html", {"listings": listings})


def categories(request):

    categories = Listings.objects.values('category').distinct()
    return render(request, "auctions/categories.html", {"categories": categories})


def category(request, category):

    listings = Listings.objects.filter(category=category)
    return render(request, "auctions/category.html", {"listings": listings, "category": category.capitalize()})


def listing_page(request, item_id):

    item = Listings.objects.get(id=item_id)
    creator_id = Listings.objects.filter(id=item_id).values_list('user', flat=True)[0]
    bid = Bids.objects.filter(listing=item).aggregate(Max('bid'))
    comments = item.comments.all()

    if item.status == "closed":
        winning_bid = Bids.objects.filter(listing=item).order_by('-bid')
        winner_id = winning_bid.first().bidder.id
    else:
        winner_id = None

    if request.user.is_authenticated:

        user = request.user

        if Watchlist.objects.filter(watcher=user, watched_listing=item):
            watcher = Watchlist.objects.filter(watcher=user, watched_listing=item).values_list('watcher', flat=True)[0]
        else:
            watcher = None
    else:

        watcher = None

    return render(request, "auctions/listing-page.html", {"item":item, "bid": bid, "comments": comments, "creator": creator_id, "watcher": watcher, "winnerid": winner_id})


@login_required(login_url="login")
def create_listing(request):

    if request.method == "POST":
        title = request.POST["title"]
        category = request.POST["category"]
        picture = request.POST["image"]
        bid = request.POST["bid"]
        description = request.POST["description"]
        user_id = request.POST["userid"]
        user = User.objects.get(id=user_id)
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%d %H:%M")
        status = "active"
        listing = Listings(user=user, title=title, description=description, start_bid=bid, picture=picture, category=category, time_stamp=time_stamp, status=status)
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create_listing.html")


@login_required(login_url="login")
def watchlist(request):

    user = request.user
    watched_listings = user.watcher.all()
    return render(request, "auctions/watchlist.html", {"listings": watched_listings})


@login_required(login_url="login")
def add_to_watchlist(request, item_id):

    listing = Listings.objects.get(id=item_id)
    user = request.user
    new_watched_item = Watchlist(watcher=user, watched_listing=listing)
    new_watched_item.save()
    return HttpResponseRedirect(reverse("watchlist"))


@login_required(login_url="login")
def remove_from_watchlist(request, item_id):

    listing = Listings.objects.get(id=item_id)
    user = request.user
    watched_item_to_delete = Watchlist.objects.filter(watcher=user, watched_listing=listing)
    watched_item_to_delete.delete()
    return HttpResponseRedirect(reverse("watchlist"))


@login_required(login_url="login")
def close_auction(request, item_id):

    item = Listings.objects.get(id=item_id)
    item.status = "closed"
    item.save()
    return redirect("listing-page", item_id)


@login_required(login_url="login")
def place_bid(request, item_id):

    user = request.user
    new_bid = int(request.POST["bid"])
    maxBid = request.POST["max-bid"]

    if maxBid == "None":
        maxBid = 0
    else:
        maxBid = int(request.POST["max-bid"])

    startBid = int(request.POST["start-bid"])
    item = Listings.objects.get(id=item_id)
    creator_id = Listings.objects.filter(id=item_id).values_list('user', flat=True)[0]
    bid = Bids.objects.filter(listing=item).aggregate(Max('bid'))
    comments = item.comments.all()

    if request.user.is_authenticated:

        user = request.user

        if Watchlist.objects.filter(watcher=user, watched_listing=item):
            watcher = Watchlist.objects.filter(watcher=user, watched_listing=item).values_list('watcher', flat=True)[0]
        else:
            watcher = None
    else:
        watcher = None

    if new_bid < startBid or new_bid <= maxBid:
        error = "Bid must exceed Price and Highest Bid!"
        return render(request, "auctions/listing-page.html", {"item":item, "bid": bid, "comments": comments, "creator": creator_id, "watcher": watcher, "error": error})

    new_bid = Bids(listing=item, bidder=user, bid=new_bid)
    new_bid.save()
    return redirect("listing-page", item_id)


@login_required(login_url="login")
def post_comment(request, item_id):

    user = request.user
    comment = request.POST["comment"]
    listing = Listings.objects.get(id=item_id)
    new_comment = Comments(commented_listing=listing, comment=comment, commenter=user)
    new_comment.save()
    return redirect("listing-page", item_id)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):

    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
