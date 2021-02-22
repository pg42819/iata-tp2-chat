from flask import Flask
from flask import session, redirect, url_for, render_template, request, flash

from app.webapp.main import tables, control, bp, forms
from app.webapp.main.forms import LoginForm, SuggestionForm
from app.chatlog import chatio
from app.chatlog.chatio import log_chat
from app.chat import bots
from app.chat.bots import Bot

current_user = None


@bp.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        bot = form.bot.data
        room = form.room.data
        control.init_bots(bot)
        if room is None or room.strip() == '':
            room = f"{name}_and_{control.current_bot().name}"
        if session['name'] is None:
            flash('Invalid name. Try again with a longer name')
            return redirect(url_for('.index'))
        session['name'] = name
        session['bot'] = bot
        session['room'] = room
        session['start_fresh'] = form.start_fresh.data
        return redirect(url_for('.chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.bot.data = session.get('bot', '')
    return render_template('index.html', form=form)


@bp.route('/chat')
def chat():
    name = session.get('name', '')
    bot = bots.get_bot(session.get('bot', ''))
    room = session.get('room', '')
    start_fresh = session.get('start_fresh', '')
    log_data = chatio.load_conversation(room, start_fresh)
    if start_fresh:
        session['start_fresh'] = False
    table_lines = log_data.to_dict('records')
    table = tables.ChatTable(table_lines)
    suggestions = control.latest_suggestions()
    return render_template('chat.html', table=table, room=room, bot_name=bot.name,
                           suggestions=suggestions)


@bp.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    suggestion_data = chatio.load_suggestions(start_fresh=False)
    table_lines = suggestion_data.to_dict('records')
    table = tables.SuggestionTable(table_lines)
    form = SuggestionForm()
    if form.validate_on_submit():
        pattern = form.pattern.data
        suggestion = form.suggestion.data
        srai = form.srai.data
        chatio.add_suggestion(pattern=pattern, message=suggestion, srai=srai)
    return render_template('suggestions.html', table=table, form=form)


