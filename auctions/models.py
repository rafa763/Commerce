from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# auction listings
class Listings(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    active = models.BooleanField(default=True) 
    category = models.CharField(max_length=50)
    image = models.TextField(blank=True, null=True)

# bids
class Bids(models.Model):
    bid = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_bid")


# comments
class Comments(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_comment")
