from flask import Flask
from flask_table import Table, Col, LinkCol, DateCol
from .utils import get_user
from datetime import datetime


class SuggestionTable(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'table-condensed']
    no_items = 'Add a suggested response'
    pattern = Col('Pattern',
                  column_html_attrs={'width': '30%', 'style': 'font-weight:bold;font-size:16'})
    suggestion = Col('Suggestion')


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

