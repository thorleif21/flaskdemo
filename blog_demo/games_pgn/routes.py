from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint, json)
from flask_login import current_user, login_required
from blog_demo import db
from blog_demo.models import Game
from blog_demo.games_pgn.forms import ImportPgnForm
from blog_demo.games_pgn.utils import save_pgn

games_pgn = Blueprint('games_pgn', __name__)


@games_pgn.route('/skak/<int:game_id>')
def skak(game_id):
    pgn = Game.query.get_or_404(game_id)
    pgn_string = pgn.pgn
    pgnlist = pgn_string.split('\n')
    return render_template('skak.html', title='skak', pgnlist=json.dumps(pgnlist))


@games_pgn.route("/pgnimport", methods=['GET', 'POST'])
@login_required
def pgnimport():
    form = ImportPgnForm()
    picture_path = url_for('static', filename='profile_pics/'+current_user.image_file)
    if form.validate_on_submit():
        if form.importpgn.data:
            texti = save_pgn(form.importpgn.data)
            flash('Flutningur tókst '+texti, 'success')
        #     debug = form.importpgn.data
        # db.session.commit()
        # flash(picture_path, 'success')
        return redirect(url_for('games_pgn.pgnimport'))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.email.data = current_user.email
    # image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('import_pgn.html', title='Pgn import', image_file=picture_path, form=form)


@games_pgn.route('/games', methods=['GET', 'POST'])
def games_list():
    if request.method == 'POST':
        search_str = request.form['search_str']
        # flash('leitar strengurinn er post '+search_str, 'success')
    else:
        search_str = request.args.get('search_str', "")
        # flash('leitar strengurinn er GET '+search_str, 'success')
    page = request.args.get('page', 1, type=int)
    if search_str == "":
        games = Game.query.order_by(Game.date_posted.desc(),  Game.white).paginate(page=page, per_page=12)
    else:
        games = Game.query.order_by(Game.white).filter(
            Game.white.like('%'+search_str+'%') | Game.black.like('%'+search_str+'%') | Game.event.like('%'+search_str+'%')).paginate(page=page, per_page=12)
    return render_template('games.html', games=games)


@games_pgn.route('/game/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    if game.sendandi != current_user:
        abort(403)
    db.session.delete(game)
    db.session.commit()
    flash('Skákinni hefur verið eytt', 'success')
    return redirect(url_for('games_pgn.games_list'))


@games_pgn.route('/chess_setup')
def chess_setup():
    return render_template('chess_setup.html', title='skak_setjaupp')
