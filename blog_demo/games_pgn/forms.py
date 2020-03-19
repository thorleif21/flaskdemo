from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField


class ImportPgnForm(FlaskForm):
    importpgn = FileField('Flytja inn pgn', validators=[FileAllowed(['pgn'])])
    submit = SubmitField('Update')
