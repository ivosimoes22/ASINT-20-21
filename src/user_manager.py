from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session

import datetime
from sqlalchemy.orm import sessionmaker
from os import path

from flask import Flask
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask import session, jsonify
from flask import request


app = Flask(__name__)


#SLQ access layer initialization
DATABASE_FILE = "db_users.sqlite"
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
        return "<User (id=%s, name=%s>" % (self.id, self.name)

    def to_dict(self):
        return {"user_id": self.id, "name": self.name}


Base.metadata.create_all(engine) #Create tables for the data models
db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)
#session = Session()

#Functions related with the db
def listUsers():
    return db_session.query(User).all()

def listUsersDict():
    users = []
    userList = listUsers()
    for user in userList:
        u = user.to_dict()
        users.append(u)
    return users


def addNewUserDB(user_id, name):
    newUser = User(id=user_id,name=name)
    try:
        db_session.add(newUser)
        db_session.commit()
        #db_session.close()
        return newUser.id
    except:
        db_session.rollback()
        return None

@app.route('/addUser', methods=['POST'] )
def addNewUser():
    if request.method == "POST":
        try:
            if addNewUserDB(request.form["id"], request.form["name"]) is not None:
                print("New User added to the Database")
            else:
                print("User Already in")
                print(listUsersDict())
        except:
            print("Error adding to user DB")
    return jsonify()       


    

if __name__ == '__main__':
    app.run(debug=True, port=4700)