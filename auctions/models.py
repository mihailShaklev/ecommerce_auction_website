from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listings(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    start_bid = models.IntegerField()
    picture = models.CharField(max_length=64)
    category = models.CharField(max_length=64)
    time_stamp = models.DateTimeField()
    status = models.CharField(max_length=64)


class Bids(models.Model):

    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid = models.IntegerField()


class Comments(models.Model):

    commented_listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=64)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")


class Watchlist(models.Model):

    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")
    watched_listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="watched_listing")
