from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import City, Base, Art

engine = create_engine('sqlite:///cityart.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


city3 = City(name="Washington")

session.add(city3)
session.commit()

city4 = City(name="Baltimore")

session.add(city4)
session.commit()

city5 = City(name="Toronto")

session.add(city5)
session.commit()

city6 = City(name="Chicago")

session.add(city6)
session.commit()

print "Art works added!"
