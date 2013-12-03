from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash


Base = declarative_base()


book_author = Table('book_author', Base.metadata,
                    Column('book_id', Integer, ForeignKey('book.id')),
                    Column('author_id', Integer, ForeignKey('author.id'))
)


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship('Book', secondary=book_author)

    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return self.name


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    authors = relationship('Author', secondary=book_author)

    def __init__(self, title, authors):
        self.title = title
        self.authors = authors

