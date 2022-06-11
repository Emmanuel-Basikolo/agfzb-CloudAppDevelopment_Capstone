from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import CarModel
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from datetime import datetime
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')



# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    print("login")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            messages.error(request,'Username or password not correct')
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print(request.method, "logout")
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    print("Registration")
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        f_name = request.POST['firstname']
        l_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug(f"Registering {f_name} {l_name} as {username}")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=f_name, last_name=l_name, password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html')
    else:
        return render(request, 'djangoapp/registration.html')


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://777cf552.eu-gb.apigw.appdomain.cloud/dealership/api/dealership"
        dealerships = get_dealers_from_cf(url)
        context = {"dealerships": dealerships}
        return render(request, 'djangoapp/dealer_list.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://777cf552.eu-gb.apigw.appdomain.cloud/dealership/api/dealership"
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        context = {
            "reviews": reviews,
            "dealer_id": dealer_id
        }
        return render(request, 'djangoapp/dealer_details.html', context)


def get_dealer_name(dealer_id):
    url = "https://777cf552.eu-gb.apigw.appdomain.cloud/dealership/api/dealership"
    dealerships = get_dealers_from_cf(url)
    for dealer in dealerships:
        if dealer.id == dealer_id:
            return dealer.full_name


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    url = "https://777cf552.eu-gb.apigw.appdomain.cloud/dealership/api/dealership"
    if request.user.is_authenticated:
        if request.method == "POST":
                form = request.POST
                review = {}
                review["dealership"] = dealer_id
                review["review"] = form["content"]
                review["purchase"] = form.get('purchasecheck', False)
                if review["purchase"] == '1':
                    car = CarModel.objects.get(pk=form["car"])
                    review["car_make"] = car.make.name
                    review["car_model"] = car.name
                    review["car_year"] = car.get_year()
                    review["purchase_date"] = datetime.strptime(form["purchase-date"], "%Y-%m-%d").strftime("%m/%d/%Y")
                    review["purchase"] = True
                review["name"] = request.user.username
                json_payload = {}
                json_payload["review"] = review
                try:
                    response = post_request(url, json_payload, dealerId=dealer_id)
                except:
                    print("Network exception occurred")
                return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else: 
            context = {
                "cars": CarModel.objects.filter(dealer_id=dealer_id),
                "dealer_id": dealer_id,
                "dealer_name": get_dealer_name(dealer_id)
            }
            return render(request, 'djangoapp/add_review.html', context)
    else:
        return redirect("/djangoapp/login")
    