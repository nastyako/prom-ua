from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import settings

engine = create_engine(settings.DB_STRING, echo=settings.DEBUG)
Session = sessionmaker(bind=engine)
session = Session()
