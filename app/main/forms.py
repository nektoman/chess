from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateRoomForm(FlaskForm):
    room = StringField('Room', validators=[DataRequired()])
    submit = SubmitField('Create')