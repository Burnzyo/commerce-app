from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.id}: {self.first_name} {self.last_name}"

class Auction(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(decimal_places=2, max_digits=6)
    description = models.CharField(max_length=280)
    image = models.URLField(blank = True)
    category = models.CharField(blank = True, max_length=64)
    creationDate = models.DateTimeField()
    user = models.ForeignKey(User, related_name="creator", on_delete=models.CASCADE)
    winner = models.ForeignKey(User, related_name="winner", on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(blank=False, default=True)
    closingDate = models.DateTimeField(blank=True, null=True)
    winnerBid = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)

    def __str__(self):
        return f"{self.id}: {self.name}"

class Bid(models.Model):
    bid = models.DecimalField(decimal_places=2, max_digits=6)
    user = models.ForeignKey(User, related_name="bidder", on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name="bidAuction", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}: Bid for {self.bid} by {self.user}"

class Comment(models.Model):
    comment = models.CharField(max_length=280)
    user = models.ForeignKey(User, related_name="commenter", on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name="commentAuction", on_delete=models.CASCADE)
    publishDate = models.DateTimeField()

    def __str__(self):
        return f"{self.id}: {self.user} made a comment in {self.auction}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, related_name="watcher", on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name="watching", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}: {self.user.first_name} is watching {self.auction.name}"