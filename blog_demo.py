# encoding=utf-8
from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '76b7abc18a2c4e52f697c080652ad7d7'

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


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
