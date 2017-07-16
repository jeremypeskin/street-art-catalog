from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import City, User, Base, Art

engine = create_engine('sqlite:///cityartwithusers.db')
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

User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')

session.add(User1)
session.commit()

city1 = City(name="Philadelphia", user_id=1)

session.add(city1)
session.commit()

city2 = City(name="New York", user_id=1)

session.add(city2)
session.commit()

city3 = City(name="Washington", user_id=1)

session.add(city3)
session.commit()

city4 = City(name="Baltimore", user_id=1)

session.add(city4)
session.commit()

city5 = City(name="Toronto", user_id=1)

session.add(city5)
session.commit()

city6 = City(name="Chicago", user_id=1)

session.add(city6)
session.commit()

print "Art works added!"
