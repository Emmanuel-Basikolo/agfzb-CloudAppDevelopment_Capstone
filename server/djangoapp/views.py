from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

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
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            # return render(request, 'djangoapp/index', context)
            messages.error(request,'Username or password not correct')
            return redirect('djangoapp:index')
    else:
        # return render(request, 'djangoapp/index', context)
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://710cbbc6.eu-gb.apigw.appdomain.cloud/dealership/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)

        # Concat all dealer's short name
        context = {"dealerships": dealerships}

        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_list.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://710cbbc6.eu-gb.apigw.appdomain.cloud/review/api/review"
        
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        context = {
            "reviews": reviews,
            "dealer_id": dealer_id
            }

        return render(request, 'djangoapp/dealer_details.html', context)


def get_dealer_name(dealer_id):
    url = "https://710cbbc6.eu-gb.apigw.appdomain.cloud/dealership/api/dealership"
    # Get dealers from the URL
    dealerships = get_dealers_from_cf(url)

    # Filter dealer by it's id and retrieve it's full name
    # full_name = [x for x in dealerships if x['id'] == dealer_id]
    for dealer in dealerships:
        if dealer.id == dealer_id:
            return dealer.full_name


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    url = "https://710cbbc6.eu-gb.apigw.appdomain.cloud/review/api/review"
    # check if user is authenticated because only authenticated users can post reviews for a dealer.
    if request.user.is_authenticated:
        # If request is POST, update the json_payload["review"] to use the actual values obtained from the review form
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
                    # If any error occurs
                    print("Network exception occurred")
                return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        # If request is GET, query the cars with the dealer id to be reviewed
        # The queried cars will be used in the <select> dropdown.
        else: 
            context = {
                "cars": CarModel.objects.filter(dealer_id=dealer_id),
                "dealer_id": dealer_id,
                "dealer_name": get_dealer_name(dealer_id)
            }
            return render(request, 'djangoapp/add_review.html', context)
    else:
        return redirect("/djangoapp/login")
    