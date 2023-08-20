from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


# categories
class Categories(models.Model):
    name = models.CharField(max_length=50)


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

# bids
class Bids(models.Model):
    pass
"""
    bid = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_bid")
    """


# comments
class Comments(models.Model):
    pass
"""
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_comment")
    """


class Watchlist(models.Model):
    pass
"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="watchlist_listing")
"""