from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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


@login_required(login_url="/login")
def categories(request):
    categs = Categories.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categs
    })


@login_required(login_url="/login")
def category_new(request):
    if request.method == "POST":
        name = request.POST["name"]
        category = Categories(name=name)
        category.save()
        return HttpResponseRedirect(reverse("categories"))
    return render(request, "auctions/category_new.html")


@login_required(login_url="/login")
def category(request, category):
    listings = Listings.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "category": Categories.objects.get(pk=category).name,
        "listings": listings
    })


@login_required(login_url="/login")
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
    user = User.objects.get(pk=request.user.id)
    listing = Listings.objects.get(pk=id)
    if request.method == "POST":
        form_type = request.POST["listing_form"]
        if form_type == "comment":
            comment = request.POST["comment"]
            commenter = User.objects.get(pk=request.user.id)
            comment = Comments(comment=comment, listing=listing, created_by=commenter)
            comment.save()
            return HttpResponseRedirect(reverse("listing", args=(id,)))
        elif form_type == "watchlist":
            # insert into watchlist if not exists
            watchlist = Watchlist.objects.filter(user=user, listing=listing)
            if watchlist.exists():
                pass
            else:
                watchlist = Watchlist(user=user, listing=listing)
                watchlist.save()
            return HttpResponseRedirect(reverse("listing", args=(id,)))
        elif form_type == "end":
            # end listing and change active to false
            listing.active = False
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(id,)))
        elif form_type == "bid":
            bid = float(request.POST["bid"])
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
        "listing": listing,
        "current_price": current_price.bid if current_price is not None else listing.price,
        "own_listing": listing.created_by == user,
        "winner": user == current_price.created_by and listing.active == False if current_price is not None else False,
        "comments": Comments.objects.filter(listing=id).order_by("-created_at")
    })


@login_required(login_url="/login")
def bid(request, id):
    # display all the bids for a listing
    listing = Listings.objects.get(pk=id)
    bids = Bids.objects.filter(listing=id).order_by("-bid")
    return render(request, "auctions/history.html", {
        "listing": listing,
        "bids": bids
    })


@login_required(login_url="/login")
def watchlist(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listings.objects.get(pk=listing_id)
        user = User.objects.get(pk=request.user.id)
        watchlist = Watchlist.objects.filter(user=user, listing=listing)
        watchlist.delete()
        return HttpResponseRedirect(reverse("watchlist"))

    return render(request, "auctions/watchlist.html", {
        "watchlist": Watchlist.objects.filter(user=request.user.id),
    })


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
