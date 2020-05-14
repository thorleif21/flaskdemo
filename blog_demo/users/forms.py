from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from blog_demo.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Notandi', validators=[DataRequired(message='Verður að fylla út'), Length(min=2, max=20, message=u'Innsláttur verður að vera milli %i and %i stafir að lengd.' % (2, 20))])
    email = StringField('Email', validators=[DataRequired(message='Það verður að fylla út'), Email(message='Óleyfilegt póstfang')])
    password = PasswordField('Lykilorð', validators=[DataRequired(message='Það verður að fylla út')])
    confirm_password = PasswordField('Staðfesting lykilorðs',
                                     validators=[DataRequired(message='Það verður að fylla út'), EqualTo('password', message='Lykilorð verða að vera eins')])
    submit = SubmitField('Skrá')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Þessi notandi er til. Veljið annan')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Þetta póstfang er til. Veljið annað')


class LoginForm(FlaskForm):
    email = StringField('Póstfang', validators=[DataRequired(
        message='Það verður að fylla út'), Email(message='Rangt póstfang')])
    password = PasswordField('Lykilorð', validators=[DataRequired(message='Það verður að fylla út')])
    remember = BooleanField('Remember me')
    submit = SubmitField('Skrá inn')


class UpdateAccountForm(FlaskForm):
    username = StringField('Notandi', validators=[DataRequired(message='Verður að fylla út'), Length(min=2, max=20, message=u'Innsláttur verður að vera milli %i and %i stafir að lengd.' % (2, 20))])
    email = StringField('Email', validators=[DataRequired(message='Verður að fylla út'), Email(message='Óleyfilegt póstfang')])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Uppfæra')

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Þessi notandi er til. Veljið annan')

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Þetta póstfang er til. Veljið annað')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Þetta póstfang er ekki til.  Búið ti reikning')


class ResetPaawordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
