import json
import sys
import settings

from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session
app = Flask(__name__)

from sql import session, engine
from sqlalchemy import or_

from models import Book, Author
from forms import BookForm, AuthorForm
from flask_login import (UserMixin, login_required, login_user, logout_user,
                         current_user, AnonymousUserMixin)
from flask_googlelogin import GoogleLogin

users = {}

app.config.update(
    SECRET_KEY='development key',
    GOOGLE_LOGIN_SCOPES='https://www.googleapis.com/auth/userinfo.email',
    GOOGLE_LOGIN_CLIENT_ID='460812075157.apps.googleusercontent.com',
    GOOGLE_LOGIN_CLIENT_SECRET='uoACD_UVCa_dIm_VBLWb7e5B',
    GOOGLE_LOGIN_REDIRECT_URI='http://127.0.0.1:8888/oauth2callback')
googlelogin = GoogleLogin(app)


class User(UserMixin):
    def __init__(self, userinfo):
        self.id = userinfo['id']
        self.name = userinfo['name']
        self.picture = userinfo.get('picture')
        self.is_autontificated = True
        self.email = userinfo.get('email')


@app.route("/")
def index():
    authors = session.query(Author).all()
    books = session.query(Book).all()
    if isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return render_template('index.html',
                           authors=authors,
                           books=books,
                           user_name=None,
                           user_picture=None,
                           if_administrator=verify_administrator())
    else:
        return render_template('index.html',
                           authors=authors,
                           books=books,
                           user_name=current_user.name,
                           user_picture=current_user.picture,
                           if_administrator=verify_administrator())


@app.route("/book/add", methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm(request.form)
    if request.method == 'POST' and form.validate():
        book = Book(form.title.data, form.author.data)
        session.add(book)
        session.commit()
        return redirect(url_for('index'))
    return render_template('book_form.html',
                           form=form,
                           action="/book/add",
                           user_name=current_user.name,
                           user_picture=current_user.picture,
                           if_administrator=verify_administrator())


@app.route("/book/<int:book_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    form = BookForm(request.form)
    if request.method == 'GET':
        form = BookForm(request.form, session.query(Book).get(book_id))
    if request.method == 'POST' and form.validate():
        book_edited = Book(form.title.data, form.author.data)
        book_db = session.query(Book).get(book_id)
        book_db.title = book_edited.title
        book_db.authors = book_edited.authors
        session.commit()
        return redirect(url_for('index'))
    return render_template('book_form.html',
                           form=form,
                           action="/book/%s/edit" % (book_id),
                           submit_text="Save",
                           user_name=current_user.name,
                           user_picture=current_user.picture,
                           if_administrator=verify_administrator())


@app.route("/book/<int:book_id>/delete")
@login_required
def delete_book(book_id):
    book = session.query(Book).get(book_id)
    session.delete(book)
    session.commit()
    return redirect(url_for('index'))


@app.route("/author/add", methods=['GET', 'POST'])
@login_required
def add_author():
    form = AuthorForm(request.form)
    if request.method == 'POST' and form.validate():
        author = Author(form.name.data)
        session.add(author)
        session.commit()
        return redirect(url_for('index'))
    return render_template('author_form.html',
                           form=form,
                           action="/author/add",
                           user_name=current_user.name,
                           user_picture=current_user.picture,
                           if_administrator=verify_administrator())


@app.route("/author/<int:author_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_author(author_id):
    form = AuthorForm(request.form)
    if request.method == 'GET':
        form = AuthorForm(request.form, session.query(Author).get(author_id))
    if request.method == 'POST' and form.validate():
        author_edited = Author(form.name.data)
        author_db = session.query(Author).get(author_id)
        author_db.name = author_edited.name
        session.commit()
        return redirect(url_for('index'))
    return render_template('author_form.html',
                           form=form,
                           action="/author/%s/edit" % (author_id),
                           submit_text="Save",
                           user_name=current_user.name,
                           user_picture=current_user.picture,
                           if_administrator=verify_administrator())


@app.route("/author/<int:author_id>/delete")
@login_required
def delete_author(author_id):
    author = session.query(Author).get(author_id)
    session.delete(author)
    session.commit()
    return redirect(url_for('index'))


@app.route("/search_results")
def search_results():
    q = request.values['q']
    books = session.query(Book).filter(or_(Book.title.like("%"+q+"%"), Book.authors.any(Author.name.like("%"+q+"%"))))
    if isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return render_template('search_results.html',
                           books=books,
                           user_name=None,
                           user_picture=None,
                           if_administrator=verify_administrator())
    else:
        return render_template('search_results.html',
                           books=books,
                           user_name=current_user.name,
                           user_picture=current_user.picture,
                           if_administrator=verify_administrator())

def fill_db():
    Book.metadata.create_all(engine)
    with open('db.sql', 'r') as sql_file:
        for insert_line in sql_file.readlines():
            engine.execute(insert_line)

@app.route("/profile")
@login_required
def profile():
    return redirect(url_for('index'))


@app.route('/oauth2callback')
@googlelogin.oauth2callback
def login(token, userinfo, **params):
    user = users[userinfo['id']] = User(userinfo)
    login_user(user)
    flask_session['token'] = json.dumps(token)
    flask_session['extra'] = params.get('extra')
    return redirect(params.get('next', url_for('.profile')))


@app.route('/logout')
def logout():
    logout_user()
    flask_session.clear()
    return redirect(url_for('index'))

@googlelogin.user_loader
def get_user(userid):
    return users.get(userid)

def verify_administrator():
    if isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return False
    return current_user.email == settings.EMAIL_ADMINISTRATOR

if __name__ == "__main__":
    if "run" in sys.argv:
        app.run(
            debug=settings.DEBUG,
            host=settings.HOST,
            port=settings.PORT,
            )
    elif "fill_db" in sys.argv:
        fill_db()
    else:
        print("Use 'run' or 'fill_db' argument")
