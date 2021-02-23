from blog_demo import create_app
from datetime import timedelta
from flask import session

app = create_app()
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
