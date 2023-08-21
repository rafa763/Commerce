from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listings, Bids, Comments, Categories, Watchlist


def index(request):
    # all listings that are active
    listings = Listings.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def categories(request):
    categs = Categories.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categs
    })


def category_new(request):
    if request.method == "POST":
        name = request.POST["name"]
        category = Categories(name=name)
        category.save()
        return HttpResponseRedirect(reverse("categories"))
    return render(request, "auctions/category_new.html")


def category(request, category):
    listings = Listings.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "category": Categories.objects.get(pk=category).name,
        "listings": listings
    })


def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["starting_bid"]
        category = request.POST["category"]
        image = request.POST["image_url"]

        print(f"{category}")
        # create listing
        catg = Categories.objects.get(pk=category)
        listing = Listings(title=title, description=description, price=price, category=catg, created_by=User.objects.get(pk=request.user.id), image=image)
        listing.save()

        return HttpResponseRedirect(reverse("index"))
    
    categories = Categories.objects.all()
    return render(request, "auctions/create.html", {
        "categories": categories
    })


@login_required(login_url="/login")
def listing(request, id):
    if request.method == "POST":
        form_type = request.POST["listing_form"]
        if form_type == "comment":
            pass
        elif form_type == "watchlist":
            pass
        elif form_type == "end":
            # end listing and change active to false
            listing = Listings.objects.get(pk=id)
            listing.active = False
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(id,)))
        elif form_type == "bid":
            bid = float(request.POST["bid"])
            listing = Listings.objects.get(pk=id)
            current_price = Bids.objects.filter(listing=id).order_by("-bid").first()
            bidder = User.objects.get(pk=request.user.id)
            if current_price is not None:
                if bid < current_price.bid:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "current_price": current_price.bid,
                        "message": "Bid must be greater than current price."
                    })
            bid = Bids(bid=bid, listing=listing, created_by=bidder)
            bid.save()
            return HttpResponseRedirect(reverse("listing", args=(id,)))

    current_price = Bids.objects.filter(listing=id).order_by("-bid").first()
    return render(request, "auctions/listing.html", {
        "listing": Listings.objects.get(pk=id),
        "current_price": current_price.bid if current_price is not None else Listings.objects.get(pk=id).price,
        "own_listing": Listings.objects.get(pk=id).created_by == User.objects.get(pk=request.user.id),
        "winner": User.objects.get(pk=request.user.id) == current_price.created_by and Listings.objects.get(pk=id).active == False if current_price is not None else False
    })


def watchlist(request):
    return render(request, "auctions/watchlist.html")


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
