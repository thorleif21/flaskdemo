import os
import secrets
import chess.pgn
import hashlib
from flask import current_app
from blog_demo import db
from blog_demo.models import Game
from flask_login import current_user


def save_pgn(form_pgn):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pgn.filename)
    pgn_fn = random_hex + f_ext
    pgn_path = os.path.join(current_app.root_path, 'static/pgn', pgn_fn)
    form_pgn.save(pgn_path)
    pgn = open(pgn_path, encoding='latin-1')
    game = chess.pgn.read_game(pgn)
    i = 0
    ie = 0
    while(game):
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        pgn_string = game.accept(exporter)
        result = hashlib.md5(pgn_string.encode("utf-8"))
        hash_str = result.hexdigest()
        white = game.headers["White"]
        if white == "":
            white = "unknown"
        if len(white) > 30:
            white = white[0:30]
        black = game.headers["Black"]
        if black == "":
            black = "unknown"
        if len(black) > 30:
            black = black[0:30]
        event = game.headers["Event"]
        if event == "":
            event = "unknown"
        if len(event) > 30:
            event = event[0:30]
        result = game.headers["Result"]
        if result == "":
            result = "?-?"
        game_hash = Game.query.filter_by(md5str=hash_str).first()
        if game.errors == []:
            iserror = False
        else:
            iserror = True
            ie += 1
        if game_hash or iserror:
            pass
        else:
            pgn_tmp = Game(white=white, black=black, event=event, result=result, pgn=pgn_string,
                           md5str=hash_str, sendandi=current_user)
            db.session.add(pgn_tmp)
            db.session.commit()
            i += 1
        game = chess.pgn.read_game(pgn)
    os.unlink(pgn_path)
    return "Færslur eru {} Gallaðar eru {}".format(i, ie)
