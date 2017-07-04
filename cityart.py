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


# Artworks in different cities
city1 = City(name="Philadelphia")

session.add(city1)
session.commit()

art1 = Art(name="The Roots", description="A mural of the roots on South St.",
           city=city1)

session.add(art1)
session.commit()

art2 = Art(name="Ela Fitzgerald", description="A mural of Ela Fitzgerald on Locust St.",
           city=city1)

session.add(art2)
session.commit()

city2 = City(name="New York")

session.add(city2)
session.commit()

art1 = Art(name="Elephants Playing", description="A mural of the elephants playing on W. 82nd Street.",
           city=city2)

session.add(art1)
session.commit()

art2 = Art(name="Two Books", description="A mural of two books in Chelsea.",
           city=city2)

session.add(art2)
session.commit()

print "Art works added!"
