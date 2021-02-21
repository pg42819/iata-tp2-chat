from flask import Flask
from flask_table import Table, Col, LinkCol, DateCol
from .utils import get_user
from datetime import datetime

# Format 'semicolon;separated;list' to 'comma, separated, list'


class SemiColonListCol(Col):
    def td_format(self, content):
        return ', '.join(content.split(';'))


# Format date time our own way because the flask_table one fails without locale settings
class CustomDateTimeCol(Col):
    def td_format(self, content):
        if content:
            return content.strftime("%b %d %Y")
        else:
            return ''


# Display properties of object as a table of Attribute, Value
class ObjectTable(Table):
    classes = ['table', 'table-bordered', 'table-condensed']
    attribute = Col('Attribute',  column_html_attrs={'width': '20%', 'style': 'font-weight:bold;font-size:16'})
    value = Col('Value')

# List games as a table with some of the columns
class GamesTable(Table):
    # Add bootstrap classes
    classes = ['table', 'table-striped', 'table-bordered', 'table-condensed']
    id = Col('Id', show=False)
    appid = Col('AppId')
    # name = Col('Title')
    # name = LinkCol('Title', 'view', url_kwargs=dict(url='https://www.google.com', appid='appid'),attr='foo')
    name = LinkCol('Title', 'main.game', url_kwargs=dict(appid='appid'), attr='name')
    release_date = CustomDateTimeCol('Release Date')
    developer = Col('Developer')
    publisher = Col('Publisher')
    platforms = SemiColonListCol('Platforms')
    # required_age = Col('Age')
    categories = SemiColonListCol('Categories')
    genres = SemiColonListCol('Genres')

    # Add these if we want later, but they make the table too wide
    # steamspy_tags = SemiColonListCol('Tags')
    # achievements = db.Column(db.Integer)
    # positive_ratings = db.Column(db.Integer)
    # negative_ratings = db.Column(db.Integer)
    # average_playtime = db.Column(db.Integer)
    # median_playtime = db.Column(db.Integer)
    # Should really be 2 columns for the min-max owners range - but use a string for simpler csv
    # owners = db.Column(db.String(255))
    # price = db.Column(db.Numeric(10, 2))

# List games as a table with some of the columns
class LogTable(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'table-condensed']
    date = Col('Date')
    time = Col('Time')
    user = Col('user')
    rating = Col('Rating')
    comment = Col('Comment')
# List games as a table with some of the columns

# Format date time our own way
class CustomDateTimeCol(Col):
    def td_format(self, content):
        if content:
            return content.strftime("%H:%M")
        else:
            return ''

class ChatTable(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'table-condensed']
    no_items = 'Say something'
    user = Col('User',
               column_html_attrs={'width': '14%', 'style': 'font-weight:bold;font-size:16'})
    time = CustomDateTimeCol('Time',
        column_html_attrs={'width': '10%', 'style': 'font-weight:light;font-size:16'})
    message = Col('Message')

    def get_tr_attrs(self, item):
        user = get_user(item['user'])
        if user is not None:
            return {"class": user.color}
        else:
            return {}

