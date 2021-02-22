from collections import OrderedDict
from random import random
from time import sleep
from typing import List

import flask
from flask import session
from flask_socketio import emit

from app.chat import bots
from app.chat.bots import Bot
from app.chatlog.chatio import log_chat
JS_ESCAPES = {
    '\\': '\\u005C',
    '\'': "",
    '"': '',
}
# Escape every ASCII character with a value less than 32.
JS_ESCAPES.update(('%c' % z, '\\u%04X' % z) for z in range(32))

_current_bot: Bot = None
_suggestion_bots: List[Bot] = list()
_last_bot_response: str = None

# Dict of suggestions keying to the bot so as to avoid duplicate suggestions
_suggestions: OrderedDict = OrderedDict()


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
    global _current_bot
    if _current_bot is None:
        _current_bot = bots.get_bot(session['bot'])
    return _current_bot


def suggestion_bots() -> List[Bot]:
    if len(_suggestion_bots) == 0:
        init_bots(session['bot'])
    return _suggestion_bots


def emit_msg(type, room, user, msg):
    message = f"{user}:{msg}"
    emit(type, {'msg': message}, room=room)


def record_message(room, user, msg):
    # store the message
    log_chat(room, user, msg)
    emit_msg('message', room, user, msg)


def update_suggestions(message):
    global _suggestions
    global _custom_suggestion
    for bot in suggestion_bots():
        suggestion = bot.respond(message)
        flask.current_app.logger.info(f"{bot.name} suggests: {suggestion}")
        # using a dict to ensure no duplicate suggestions but skip empties
        if suggestion is not None:
            suggestion = escapejs(suggestion)
            if len(suggestion) > 0:
                _suggestions[suggestion] = bot
    return _suggestions


def escapejs(value):
    value = str(value).strip()
    escaped = "".join(JS_ESCAPES.get(l, l) for l in value)
    return escaped


def react_to_message(room, user, msg):
    global _last_bot_response
    record_message(room=room, user=user, msg=msg)
    """ React to the users latest message, by asking a Bot to respond """
    bot = current_bot()
    bot_response = bot.respond(msg)
    dramatic_pause()
    # Give some suggested responses to the bot message
    update_suggestions(bot_response)
    _last_bot_response = bot_response
    record_message(room=room, user=bot.name, msg=bot_response)
    # emit_msg('bot', room, user, msg)


def dramatic_pause():
    """ Pause a random time up to a few seconds. See config.py to change the value """
    max_seconds = flask.current_app.config['MAX_PAUSE_SECONDS']
    sleep(random() * max_seconds)


def clear_suggestions():
    _suggestions.clear()
    print(f"cleared suggestions now: {len(_suggestions)}")


def latest_suggestions(last_message=None):
    """ get the latest suggestions to return to the user"""
    if len(_suggestions) == 0:
        if _last_bot_response is not None:
            return update_suggestions(_last_bot_response)
        elif last_message is not None:
            return update_suggestions(last_message)
    return _suggestions

