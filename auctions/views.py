from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django import forms
from .models import *
from datetime import date, datetime 
from django.contrib.auth.decorators import login_required

from .models import User

class CreationForm(forms.Form):
    title = forms.CharField(required = True, widget = forms.TextInput(attrs={
        "class": "form-control mb-2",
        "placeholder": "Auction Title"
    }))
    description = forms.CharField(required = True, widget = forms.Textarea(attrs={
        "class": "form-control mb-4",
        "placeholder": "Write a brief descripcion"
    }))
    startingBid = forms.DecimalField(required=True, label="Starting Bid:", decimal_places=2, widget=forms.TextInput(attrs={
        "class": "form-control mb-2",
        "placeholder": "Starting Bid"
    }))
    image = forms.CharField(required = False, widget = forms.TextInput(attrs={
        "class": "form-control mb-2",
        "placeholder": "Image URL"
    }))
    category = forms.CharField(required = False, widget = forms.TextInput(attrs={
        "class": "form-control mb-2",
        "placeholder": "Category"
    }))

class CommentForm(forms.Form):
    comment = forms.CharField(required = True, label="", widget = forms.TextInput(attrs={
        "class": "form-control mb-3",
        "placeholder": "Place your comment (Max 300 Chars).",
        "maxlength": "300"
    }))

def index(request):
    auctionsList = Auction.objects.filter(active = True)
    reversedAuctionList = auctionsList[::-1]
    return render(request, "auctions/index.html", {
        "auctions": reversedAuctionList
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
        firstName = request.POST["firstName"]
        lastName = request.POST["lastName"]

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
            user.first_name = firstName
            user.last_name = lastName
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def createListing(request):
    userId = request.user.id
    user1 = User.objects.get(pk = userId)
    if request.method == "POST":
        form = CreationForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description1 = form.cleaned_data["description"]
            startingBid = form.cleaned_data["startingBid"]
            image1 = form.cleaned_data["image"]
            if image1 is None or image1 == "":
                image1 = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"
            category1 = form.cleaned_data["category"]
            now = datetime.now()
            creationDate1 = now
            auction = Auction(name=title, price=startingBid, description=description1, image=image1, category=category1, creationDate=creationDate1, user=user1)
            auction.save()
            return redirect(reverse("index"))
    return render(request, "auctions/create.html", {
        "form": CreationForm()
    })

def getHigherBid(auctionId):
    bids = Bid.objects.filter(auction = auctionId)
    realbids = []
    for i in range(0, len(bids)):
        realbids.append(bids[i].bid)
    higher = 0.0
    for bid in realbids:
        if bid > higher:
            higher = bid
    return higher

def getRealBids(auctionId):
    bids = Bid.objects.filter(auction = auctionId)
    realbids = []
    for i in range(0, len(bids)):
        realbids.append(bids[i].bid)
    return realbids

def isWatching(userId, auction):
    watching = Watchlist.objects.filter(user = userId, auction = auction)
    if watching.count() > 0:
        return True
    else: 
        return False

def getAuction(request, auctionId):
    bids = getRealBids(auctionId)
    auction = Auction.objects.get(pk = auctionId)
    comments = Comment.objects.filter(auction = auctionId)
    if comments.count() > 0:
        comments = comments[::-1]
    if auction.active == False:
        url = f"/closed/{auctionId}"
        return redirect(url)
    if auction.user.id == request.user.id:
        if "comment" in request.POST:
            return postComment(request, auctionId, len(bids))
        return render(request, "auctions/auction.html", {
        "auction": Auction.objects.get(pk=auctionId),
        "price": getHigherBid(auctionId),
        "numberofbids": len(bids),
        "owner": True,
        "comments": comments,
        "form": CommentForm()
    })
    elif isWatching(request.user.id, auction):
        if request.method == "POST":
            if "newbid" in request.POST:
                return newPlaceBid(request, auctionId, len(bids))
            elif "removefromwatchlist" in request.POST:
                return removeFromWatchlist(request, auctionId, len(bids))
            elif "comment" in request.POST:
                return postComment(request, auctionId, len(bids))
        return render(request, "auctions/auction.html", {
        "auction": Auction.objects.get(pk=auctionId),
        "price": getHigherBid(auctionId),
        "numberofbids": len(bids),
        "alreadyWatching": True,
        "comments": comments,
        "form": CommentForm()
    })
    elif "newbid" in request.POST:
        return newPlaceBid(request, auctionId, len(bids))
    elif "addtowatchlist" in request.POST:
        return addToWatchlist(request, auctionId, len(bids))
    elif "comment" in request.POST:
        return postComment(request, auctionId, len(bids))
    return render(request, "auctions/auction.html", {
        "auction": Auction.objects.get(pk=auctionId),
        "price": getHigherBid(auctionId),
        "numberofbids": len(bids),
        "comments": comments,
        "form": CommentForm()
    })

def newPlaceBid(request, auctionId, numberOfBids):
    auction = Auction.objects.get(pk = auctionId)
    actualBid = getHigherBid(auctionId)
    newbid = request.POST["newbid"]
    comments = Comment.objects.filter(auction = auctionId)
    if comments.count() > 0:
        comments = comments[::-1]
    if not request.user.is_authenticated:
        return render(request, "auctions/auction.html", {
            "auction": Auction.objects.get(pk=auctionId),
            "price": getHigherBid(auctionId),
            "numberofbids": numberOfBids,
            "message": "You must be logged in to place a bid.",
            "comments": comments,
            "form": CommentForm()
        })
    else: 
        if newbid == None or newbid == 0 or newbid == "":
            if isWatching(request.user.id, auction):
                return render(request, "auctions/auction.html", {
                    "auction": Auction.objects.get(pk=auctionId),
                    "price": getHigherBid(auctionId),
                    "numberofbids": numberOfBids,
                    "message": "You can not place a bid of $0.00",
                    "alreadyWatching": True,
                    "comments": comments,
                    "form": CommentForm()
                })
            else: 
                return render(request, "auctions/auction.html", {
                    "auction": Auction.objects.get(pk=auctionId),
                    "price": getHigherBid(auctionId),
                    "numberofbids": numberOfBids,
                    "message": "You can not place a bid of $0.00",
                    "comments": comments,
                    "form": CommentForm()
                })
        else: 
            newbid = float(request.POST["newbid"])
            if newbid <= actualBid or newbid < float(auction.price):
                if isWatching(request.user.id, auction):
                    return render(request, "auctions/auction.html", {
                        "auction": Auction.objects.get(pk=auctionId),
                        "price": getHigherBid(auctionId),
                        "numberofbids": numberOfBids,
                        "message": "You can not place a bid that is lower or equal than the actual price",
                        "alreadyWatching": True,
                        "comments": comments,
                        "form": CommentForm()
                    })
                else:
                    return render(request, "auctions/auction.html", {
                        "auction": Auction.objects.get(pk=auctionId),
                        "price": getHigherBid(auctionId),
                        "numberofbids": numberOfBids,
                        "message": "You can not place a bid that is lower or equal than the actual price",
                        "comments": comments,
                        "form": CommentForm()
                    })
            createNewBid = Bid(bid = newbid, user = request.user, auction = auction)
            createNewBid.save()
    if isWatching(request.user.id, auction):
        return render(request, "auctions/auction.html", {
            "auction": Auction.objects.get(pk=auctionId),
            "price": getHigherBid(auctionId),
            "numberofbids": numberOfBids,
            "bidplaced": "Your bid was placed.",
            "alreadyWatching": True,
            "comments": comments,
            "form": CommentForm()
        })
    else: 
        return render(request, "auctions/auction.html", {
            "auction": Auction.objects.get(pk=auctionId),
            "price": getHigherBid(auctionId),
            "numberofbids": numberOfBids,
            "bidplaced": "Your bid was placed.",
            "comments": comments,
            "form": CommentForm()
        })

def addToWatchlist(request, auctionId, numberOfBids):
    comments = Comment.objects.filter(auction = auctionId)
    if comments.count() > 0:
        comments = comments[::-1]
    if not request.user.is_authenticated:
        return render(request, "auctions/auction.html", {
            "auction": Auction.objects.get(pk=auctionId),
            "price": getHigherBid(auctionId),
            "numberofbids": numberOfBids,
            "message": "You must be logged to add an auction to your watchlist.",
            "comments": comments,
            "form": CommentForm()
        })
    if request.method=="POST":
        auction = Auction.objects.get(pk = auctionId)
        objectToAdd = Watchlist(user = request.user, auction = auction)
        objectToAdd.save()
        return render(request, "auctions/auction.html", {
                "auction": Auction.objects.get(pk=auctionId),
                "price": getHigherBid(auctionId),
                "numberofbids": numberOfBids,
                "watchlist": "Correctly added to the Watchlist.",
                "alreadyWatching": True,
                "comments": comments,
                "form": CommentForm()
            })

def removeFromWatchlist(request, auctionId, numberOfBids):
    comments = Comment.objects.filter(auction = auctionId)
    if comments.count() > 0:
        comments = comments[::-1]
    if request.method=="POST":
        auction = Auction.objects.get(pk = auctionId)
        todelete = Watchlist.objects.get(user = request.user, auction = auction)
        todelete.delete()
        return render(request, "auctions/auction.html", {
                "auction": Auction.objects.get(pk=auctionId),
                "price": getHigherBid(auctionId),
                "numberofbids": numberOfBids,
                "watchlist": "Correctly removed from the Watchlist.",
                "comments": comments,
                "form": CommentForm()
            })

def watchlist(request):
    watchlist = Watchlist.objects.filter(user = request.user.id).values("auction")
    auctions = []
    for auction in watchlist:
        auctions.append(Auction.objects.get(pk = auction["auction"]))
    auctions = auctions[::-1]
    return render(request, "auctions/watchlist.html", {
        "auctions": auctions
    })

def closeAuction(request, auctionId):
    auction = Auction.objects.get(pk=auctionId)
    bids = Bid.objects.filter(auction=auctionId)
    creator = f"{User.objects.get(pk = request.user.id).first_name} {User.objects.get(pk = request.user.id).last_name}"
    comments = Comment.objects.filter(auction = auctionId)
    if comments.count() > 0:
        comments = comments[::-1]
    if bids.count() > 0:
        winner = bids.get(bid=getHigherBid(auctionId))
        higherBid = getHigherBid(auctionId)
        emptyBid = False
    else:
        winner = "There is not a winner since nobody bid."
        higherBid = "Nobody bid in this auction."
        emptyBid = True
    if request.method == "POST":
        closingDate = datetime.now()
        if bids.count() > 0:
            auction.winner = winner.user
            auction.active = False
            auction.winnerBid = getHigherBid(auctionId)
            auction.closingDate = closingDate
            auction.save()
            return render(request, "auctions/closedAuction.html", {
                "auction": auction,
                "higherbid": higherBid,
                "numberofbids": len(bids),
                "createdby": creator,
                "winner": winner,
                "emptybid": emptyBid,
                "closed": True,
                "comments": comments
            })
        else: 
            auction.active = False
            auction.closingDate = closingDate
            auction.winnerBid = getHigherBid(auctionId)
            auction.save()
            return render(request, "auctions/closedAuction.html", {
                "auction": auction,
                "higherbid": higherBid,
                "numberofbids": len(bids),
                "createdby": creator,
                "winner": winner,
                "emptybid": emptyBid,
                "closed": True,
                "comments": comments
            })
    return render(request, "auctions/closedAuction.html", {
        "auction": auction,
        "higherbid": higherBid,
        "numberofbids": len(bids),
        "createdby": creator,
        "winner": winner,
        "emptybid": emptyBid,
        "comments": comments
    })

def closed(request):
    closedAuctions = Auction.objects.filter(active = False)
    reversedAuctionList = closedAuctions[::-1]
    return render(request, "auctions/closed.html", {
        "auctions": reversedAuctionList
    })

def categories(request, category):
    auctions = Auction.objects.filter(category = category, active = True)
    auctions = auctions[::-1]
    return render(request, "auctions/category.html", {
        "auctions": auctions,
        "category": category
    })

def listCategories(request):
    auctions = Auction.objects.filter(active = True).values("category").distinct()
    categories = []
    for auction in auctions:
        categories.append(auction["category"])
    return render(request, "auctions/listCategories.html", {
        "categories": categories
    })

def postComment(request, auctionId, numberOfBids):
    comments = Comment.objects.filter(auction = auctionId)
    if comments.count() > 0:
        comments = comments[::-1]
    auction = Auction.objects.get(pk = auctionId)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return render(request, "auctions/auction.html", {
                "auction": auction,
                "price": getHigherBid(auctionId),
                "numberofbids": numberOfBids,
                "comments": comments,
                "message": "You should be logged in to post comments.",
                "form": CommentForm()
            })
        form = CommentForm(request.POST)
        if form.is_valid():
            now = datetime.now()
            user = User.objects.get(pk = request.user.id)
            comment = form.cleaned_data["comment"]
            newcomment = Comment(user = user, auction = auction, comment = comment, publishDate = now)
            newcomment.save()
            return redirect(reverse("auction", args=[auctionId]))
    return render(request, "auctions/auction.html", {
        "auction": auction,
        "price": getHigherBid(auctionId),
        "numberofbids": numberOfBids,
        "comments": comments,
        "form": CommentForm()
    })