# The configuration code is simply used to import all of the necessary modules

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Below is the "class code".  This is the object-oriented representation of our
# table as a python class.  It extends the base class


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Art(Base):
    __tablename__ = 'art'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    city_id = Column(Integer,ForeignKey('city.id'))
    city = relationship(City)

# insert at end of file.  This code points to the database #
engine = create_engine(
    'sqlite:///cityart.db')

# This code goes into the database and creates new tables
Base.metadata.create_all(engine)
