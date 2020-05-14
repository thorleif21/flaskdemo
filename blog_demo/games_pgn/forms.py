from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField


class ImportPgnForm(FlaskForm):
    importpgn = FileField('Hlaða inn pgn', validators=[FileAllowed(['pgn']), FileRequired()])
    submit = SubmitField('Uppfæra')
