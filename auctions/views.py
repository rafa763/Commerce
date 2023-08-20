from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listings, Bids, Comments, Categories, Watchlist


def index(request):
    # all listings that are active
    listings = Listings.objects.filter(active=True)
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


def listing(request, id):
    return render(request, "auctions/listing.html")


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
