from random import random
from time import sleep
from typing import List

import flask
from flask import session
from flask_socketio import emit

from app.chat import bots
from app.chat.bots import Bot
from app.chatlog.chatlog import log_chat

_current_bot: Bot = None
_suggestion_bots: List[Bot] = list()
_suggestions: List[str] = list()


def init_bots(current_aiml_name=None):
    global _current_bot
    global _suggestion_bots

    if current_aiml_name is None:
        current_aiml_name = session['bot']
    _current_bot = bots.get_bot(current_aiml_name)
    flask.current_app.logger.info(f"Setting current bot to {current_aiml_name}")
    all_bots = bots.get_all_bots()
    if all_bots:
        for aiml_name, bot in all_bots.items():
            if aiml_name != current_aiml_name:
                add_suggestion_bot(bot)
    # load a copy of the current bot to suggest answers to itself as the secondary answer
    add_suggestion_bot(bots.load_bot(current_aiml_name))


def add_suggestion_bot(bot):
    # not the bot we're talking to, make it a suggestion bot
    # first tell it who it is responding to (not me, but the other bot, because
    # its suggesting how _I_ respond to that bot)
    bot.set_correspondent_name(_current_bot.name)
    _suggestion_bots.append(bot)
    flask.current_app.logger.info(f"Added suggestion bot: {bot.aiml_name}")



def current_bot() -> Bot:
    return _current_bot


def suggestion_bots() -> List[Bot]:
    return _suggestion_bots


def emit_message(room, user, msg):
    log_chat(room, user, msg)
    # emit the message to update the UI
    message = f"{user}:{msg}"
    emit('message', {'msg': message}, room=room)
    # print(f'Emitted message from {user}: {msg}')


def update_suggestions(message):
    global _suggestions
    for bot in _suggestion_bots:
        suggestion = bot.respond(message)
        flask.current_app.logger.info(f"{bot.name} suggests {suggestion}")
        _suggestions.append(suggestion)


def react_to_message(room, user, msg):
    """ React to the users latest message, by asking a Bot to respond """
    bot = current_bot()
    bot_response = bot.respond(msg)
    update_suggestions(bot_response)
    dramatic_pause()
    emit_message(room=room, user=bot.name, msg=bot_response)


def dramatic_pause():
    """ Pause a random time up to a few seconds. See config.py to change the value """
    max_seconds = flask.current_app.config['MAX_PAUSE_SECONDS']
    sleep(random() * max_seconds)


def latest_suggestions(max):
    """ get the latest suggestions to return to the user"""
    suggestions = []
    for i in range(max):
        if _suggestions:
            suggestions.append(_suggestions.pop())
    return suggestions

