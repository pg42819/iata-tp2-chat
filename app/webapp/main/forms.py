from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

from app.chat import bots
from app.chatlog import chatio

class LoginForm(FlaskForm):
    """Accepts a nickname and room."""
    name = StringField('Your name', validators=[DataRequired(),
                                                Regexp(r'^[\w.@+-]*$'),
                                                Length(min=0, max=25)])
    bot = SelectField('Chat With', choices=bots.get_bot_choices())
    room = StringField('Room name',
                       validators=[Regexp(r'^[\w.@+-]*$'), Length(min=0, max=25)],
                       description="Simple name, no spaces. Defaults to You_and_Bot",
                       render_kw={"placeholder": "You_and_Alice"})
    start_fresh = BooleanField('Start fresh')
    submit = SubmitField('Enter Chatroom')

class ChatForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Say it!')


class SuggestionForm(FlaskForm):
    pattern = StringField(label='Pattern:', validators=[DataRequired()], description=
                          'Use wildcards for AIML-like patterns')
    suggestion = StringField(label='Suggested response:', validators=[DataRequired()])
    srai = BooleanField(label='Wrap in SRAI')
    submit = SubmitField('Add suggestion')

    def validate_pattern(self, pattern):
        existing = chatio.get_suggestion_for(pattern=pattern.data)
        if existing is not None:
            raise ValidationError('Please use a different pattern - this one is already used.')

