from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp

from app.chat import bots


class LoginForm(FlaskForm):
    """Accepts a nickname and room."""
    name = StringField('Your name', validators=[DataRequired()])
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
