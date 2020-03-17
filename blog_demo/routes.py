import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, json
from blog_demo.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ImportPgnForm, RequestResetForm, ResetPaawordForm
from blog_demo import app, db, bcrypt, mail
from blog_demo.models import User, Post, Game
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import chess.pgn
import hashlib


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='about')


@app.route('/skak/<int:game_id>')
def skak(game_id):
    pgn = Game.query.get_or_404(game_id)
    pgn_string = pgn.pgn
    pgnlist = pgn_string.split('\n')
    return render_template('skak.html', title='skak', pgnlist=json.dumps(pgnlist))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,  password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created You are now able to log in !", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend="New Post")


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend="Update Post")


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('your post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(
        Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def save_pgn(form_pgn):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pgn.filename)
    pgn_fn = random_hex + f_ext
    pgn_path = os.path.join(app.root_path, 'static/pgn', pgn_fn)
    form_pgn.save(pgn_path)
    pgn = open(pgn_path)
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


@app.route("/pgnimport", methods=['GET', 'POST'])
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
        return redirect(url_for('pgnimport'))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.email.data = current_user.email
    # image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('import_pgn.html', title='Pgn import', image_file=picture_path, form=form)


@app.route('/games', methods=['GET', 'POST'])
def games():
    if request.method == 'POST':
        search_str = request.form['search_str']
#        flash('leitar strengurinn er '+search_str, 'success')
    else:
        search_str = request.args.get('search_str', "")
#        flash('leitar strengurinn er '+search_str, 'success')
    page = request.args.get('page', 1, type=int)
    if search_str == "":
        games = Game.query.order_by(Game.white).paginate(page=page, per_page=12)
    else:
        games = Game.query.order_by(Game.white).filter(
            Game.white.like('%'+search_str+'%') | Game.black.like('%'+search_str+'%') | Game.event.like('%'+search_str+'%')).paginate(page=page, per_page=12)
    return render_template('games.html', games=games)


@app.route('/game/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    if game.sendandi != current_user:
        abort(403)
    db.session.delete(game)
    db.session.commit()
    flash('Skákinni hefur verið eytt', 'success')
    return redirect(url_for('games'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='reply@demo.com', recipients=[user.email])
    msg.body = f''' To reset your password visit thr following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and nochanges will be made
    '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('A email has been sent to seset your password', 'info')
        return redirect(url_for('Login'))
    return render_template('request_reset.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPaawordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated. You are now able to log in !", "success")
        return redirect(url_for('login'))

    return render_template('reset_token.html', title='Reset Password', form=form)
