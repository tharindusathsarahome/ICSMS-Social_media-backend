import requests
from facebook import GraphAPI

FACEBOOK_USER_TOKEN = "EAADezGvsg98BO9I3RmARTEUX483cdV2Tbbx04wuHcH0Omews5PFNABqRcZAkZBhMAHgotUluhbrO5wWX8YeUhlaJhg5KWgdWVEryDAqPahgVwDIYXYyApXeuzO7PZBwpXoMKc8IGpCoHuAe5e2CX4BwMbQTVzzm5ZCdHe0ttDrK1ec5dm1q7EzvlKFZCX5vAqVy8mAPg0QQ8ZC3C1lqwZDZD"
FACEBOOK_API_VERSION = "19.0"

response = requests.post(
    url="https://graph.facebook.com/v" + FACEBOOK_API_VERSION + "/me?fields=accounts",
    data={
        "access_token": FACEBOOK_USER_TOKEN
    },
)
response.raise_for_status()
token = response.json()['accounts']['data'][0]['access_token']

newapi = GraphAPI(token)

comments = newapi.get_object(f"779977917565074_963492651794087", fields='id,message,created_time,from,likes.summary(true),comments.summary(true)')

print(comments)