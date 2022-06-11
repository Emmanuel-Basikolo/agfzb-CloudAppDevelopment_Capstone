import requests
import json

# import related models here
from .models import CarDealer, DealerReview

# IBM Watson
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        # If any error occurs
        print("Error (Network)")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    print("POST to {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Error (Network)")        
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        try:
            dealers = json_result["dealershipList"]
            # For each dealer object
            for dealer in dealers:
                # Get its content in `doc` object

                dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                            id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                            short_name=dealer["short_name"],
                            st=dealer["st"], zip=dealer["zip"], state=dealer["state"])
                results.append(dealer_obj)
        except:
            pass

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        if "statusCode" in json_result and json_result["statusCode"] == 404:
            return results    
        else:      
            # Get the row list in JSON as dealers
            try:
                reviews = json_result["reviewsList"]
                # For each dealer object
                for review in reviews:

                    if "purchase_date" in review:
                        review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"],
                                    review=review["review"], purchase_date=review["purchase_date"], car_make=review["car_make"],
                                    car_model=review["car_model"],
                                    car_year=review["car_year"], id="")
                    else:
                        review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"],
                                    review=review["review"], purchase_date="", car_make="",
                                    car_model="",
                                    car_year="", id="")

                    sentiment = analyze_review_sentiments(review_obj.review)
                    review_obj.sentiment_score = float(sentiment["sentiment_score"])
                    review_obj.sentiment_label = sentiment["sentiment_label"]

                    results.append(review_obj)
            except:
                pass

        return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    api_key = "pxrurO62iBgUZKBc0c4yfcf_ATWe10By93_hktZUbIxV"
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/921fdebd-0bf8-4c66-9fde-63f3d0b5f3e0"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze(
        text=text,
        language='en',
        features= Features(sentiment= SentimentOptions())
    ).get_result()

    sentiment_score = str(response["sentiment"]["document"]["score"])
    sentiment_label = response["sentiment"]["document"]["label"] 

    sentiment = {
        "sentiment_score": sentiment_score,
        "sentiment_label": sentiment_label
    }

    return sentiment
