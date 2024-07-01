import requests
from facebook import GraphAPI

FACEBOOK_USER_TOKEN = "EAADezGvsg98BO1F4Og5tnnlgsyMxs4oz7X2nieXRbVpY24QxP8q039weqUUV4INvzNdpZAhYprXmDJZAHd3B3G6DtUlrgV3WylJUiXM3kHKVHFsMaGeA400MtQLZBqpZAxEXyfBZBqrszCZCHDW3QP2utt1EAqBCTNu4wXObpCZB10qPXFZBjYYmnKhmE65zV4NtDq3xSgZCNHRpbUXPLPgZDZD"
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