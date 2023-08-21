from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass


# categories
class Categories(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id}: {self.name}"


# auction listings
class Listings(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    active = models.BooleanField(default=True) 
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="category")
    image = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}: \
        description: {self.description}, price: {self.price}, at: {self.created_at}, by: {self.created_by}, cat: {self.category}, img: {self.image}"

# bids
class Bids(models.Model):
    bid = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="bidder")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_bid")

    def __str__(self):
        return f"{self.bid}: {self.created_at}, by: {self.created_by}, listing: {self.listing}"


# comments
class Comments(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_comment")

    def __str__(self):
        return f"{self.comment}: {self.created_at}, by: {self.created_by}, listing: {self.listing}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="watchlist_listing")

    def __str__(self):
        return f"{self.user}: {self.listing}"