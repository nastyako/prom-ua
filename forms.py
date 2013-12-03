from wtforms import Form, TextField, validators, PasswordField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

from sql import session
from models import Author


def get_author():
    return session.query(Author).all()


class BookForm(Form):
    title = TextField('Title', [validators.InputRequired()])
    author = QuerySelectMultipleField(query_factory=get_author)


class AuthorForm(Form):
    name = TextField('Name', [validators.InputRequired()])

