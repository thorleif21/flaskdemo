from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from blog_demo import db
from blog_demo.models import Post
from blog_demo.posts.forms import PostForm


posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    default_str = ''
    fen_str = request.args.get('fen_str', default_str)
    hvitur_str = request.args.get('hvitur_str', default_str)
    svartur_str = request.args.get('svartur_str', default_str)
    result_str = request.args.get('result_str', default_str)

    if fen_str == '':
        form = PostForm()
    else:
        form = PostForm(request.values, title=hvitur_str+'-'+svartur_str+' '+result_str, fldh=fen_str)
    if request.method == 'POST' and form.validate():

        #    if form.validate_on_submit():
        post = Post(title=form.title.data, fen1=form.fldh.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created POST', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend="New Post")


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.fldh.data = post.fen1
    return render_template('create_post.html', title='Update Post', form=form, legend="Update Post")


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('your post has been deleted', 'success')
    return redirect(url_for('main.home'))
