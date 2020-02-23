from flask import render_template, url_for, flash, redirect
from blog_demo.forms import RegistrationForm, LoginForm
from blog_demo import app
from blog_demo.models import User, Post

posts = [
    {
        'author': u'Þorleifur Einarsson',
        'title': u'Blog póstur 1',
        'content': u'Efni pósts nr 1',
        'date_posted': u'21 apríl 2019'
    },
    {
        'author': u'Jón Jónsson',
        'title': u'Blog póstur 2',
        'content': u'Efni pósts nr 2',
        'date_posted': u'22 apríl 2019'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='about')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash("Account created for {} !".format(form.username.data), "success")
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
