import requests
from facebook import GraphAPI

FACEBOOK_USER_TOKEN = "EAADezGvsg98BOwUv87rwGmfRb3dkTv3p7EFJE1vfZCxe1diOgZCvBKydRRkdjnZB8rzZBcL2z6H6ZBdQNv3WZCqepZAcqfi99TLgUzmBgm962kGS8MvrZCjxwNpJQEZCqDEPcVdR3zydndSQAAA8gxkxZBO98CstzEdyfWpB1NEs8tq4RWlj7SUm0U0TIJcYrlZCBM8fngqooZAUiTLPItDgVgZDZD"
FACEBOOK_API_VERSION = "19.0"

response = requests.get(
    url="https://graph.facebook.com/v" + FACEBOOK_API_VERSION + "/oauth/access_token",
    params={
        "grant_type": "fb_exchange_token",
        "client_id": "244969565357023",
        "client_secret": "2adb37dce72f56a469c6054f39d78324",
        "fb_exchange_token": FACEBOOK_USER_TOKEN
    },
)

access_token = response.json()

print(access_token)

# https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived