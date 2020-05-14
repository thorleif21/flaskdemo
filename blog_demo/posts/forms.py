from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Titill', validators=[DataRequired(message='Insláttar krafist')])
    content = TextAreaField('Efni', validators=[DataRequired(message='Insláttar krafist')])
    fldh = HiddenField('FieldHidden')
    orient = HiddenField('OrientHidden')
    submit = SubmitField('Skrá')
