from dataclasses import dataclass

from collections import OrderedDict

USER_COLORS = [
    "info",     # blue
    "active",   # grey
    "success",  # green
    "warning"   # yellow
]

users = OrderedDict() # maintain order for colors
current_user = None

# data class holding information about a user
@dataclass
class User:
    name: str
    color: str

def get_user(username):
    username = username.strip()
    if username not in users:
        next_color = USER_COLORS[len(users) % len(USER_COLORS)]
        user = User(username, next_color)
        users[username] = user
        return user
    else:
        return users[username]

