from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session

import datetime
from sqlalchemy.orm import sessionmaker
from os import path


#SLQ access layer initialization
DATABASE_FILE = "database.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    id = Column(String, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<User (id=%s, Name=%s>" % (self.id, self.name)

    def to_dict(self):
        return {"user_id": self.id, "name": self.name}


Base.metadata.create_all(engine) #Create tables for the data models
db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)
#session = Session()

def listUsers():
    return db_session.query(User).all()

def listUsersDict():
    users = []
    userList = listUsers()
    for user in userList:
        u = user.to_dict()
        users.append(u)
    return users


def addNewUser(user_id, name):
    newUser = User(id=user_id,name=name)
    try:
        db_session.add(newUser)
        db_session.commit()
        #db_session.close()
        return newUser.id
    except:
        db_session.rollback()
        return None