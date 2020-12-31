import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import scoped_session
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from os import path
from flask import Flask
from flask import jsonify
from flask import request

logs = "http://127.0.0.1:4600/"

app = Flask(__name__)


#SLQ access layer initialization
DATABASE_FILE = "db_users.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of the User Table
class User(Base):
    __tablename__ = 'User'
    id = Column(String, primary_key=True)
    name = Column(String,nullable=False)
    views = Column(Integer, default=0)
    videos = Column(Integer, default=0)
    questions = Column(Integer, default=0)
    answers = Column(Integer, default=0)

    def __repr__(self):
        return "<User (id=%s, name=%s>, views=%d, videos=%d, questions=%d, answers=%d)" % (self.id, self.name, self.views, self.videos, self.questions, self.answers)

    def to_dict(self):
        return {"user_id": self.id, "name": self.name, "views": self.views, "n_videos": self.videos, "n_questions": self.questions, "n_answers": self.answers}


Base.metadata.create_all(engine) #Create tables for the data models
db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)
#session = Session()


#Functions related with the User DataBase

#Listing of all user events
def listUsers():
    return db_session.query(User).all()

#Listing of user events to dictionary
def listUsersDict():
    users = []
    userList = listUsers()
    for user in userList:
        u = user.to_dict()
        users.append(u)
    return users

#Querying the User Table to find a specific user corresponding to "id"
def getUserDB(user_id):
    user = db_session.query(User).filter(User.id==user_id).first()
    return user.to_dict()

#Adding the new user event to the User Table
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

#Incrementing the number of views on the user "id"
def newView(id):
    u = db_session.query(User).filter(User.id==id).first()
    u.views +=1
    n_view = u.views
    db_session.commit()
    db_session.close()
    print(listUsers())
    return n_view

#Incrementing the number of videos posted by user "id"
def newVideo(id):
    u = db_session.query(User).filter(User.id==id).first()
    u.videos +=1
    n_videos = u.videos
    db_session.commit()
    db_session.close()
    print(listUsers())
    return n_videos

#Incrementing the number of questions posted by user "id"
def newQuestion(id):
    u = db_session.query(User).filter(User.id==id).first()
    u.questions +=1
    n_questions = u.questions
    db_session.commit()
    db_session.close()
    print(listUsers())
    return n_questions

#Incrementing the number of answers posted by user "id"
def newAnswer(id):
    u = db_session.query(User).filter(User.id==id).first()
    u.answers +=1
    n_answers = u.answers
    db_session.commit()
    db_session.close()
    print(listUsers())
    return n_answers


#Endpoint functions

@app.before_request
def beforeRequest():
    log = {}
    log["timestamp"] = str(datetime.now())
    log["request"] = str(request.url) + ' [' + str(request.method) + ']'
    url = logs+'store/message_events'

    try:
        resp = requests.post(url=url, data=log)
    except:
        print("Error in Post")
    return

#Adding new user (User Creation Events)
@app.route('/user/add', methods=['POST'] )
def addNewUser():
    try:
        if addNewUserDB(request.form["id"], request.form["name"]) is not None:
            print("New User added successfully.")

            data = {"timestamp": str(datetime.now()), "d_type": "User", "user": request.form["id"]}
            data["d_content"] = 'Username: ' + request.form["id"] + '; Name: ' + request.form["name"]

            try:
                resp = requests.post(url=logs+'store/data_events', data=data)
            except:
                print("Error in POST")

        else:
            print("User already in the DataBase.")
            print(listUsersDict())
    except:
        print("Error adding to User DataBase.")
    return jsonify()

#Querying the User Table
@app.route('/user/get/', methods=["GET"])
def getUser():
    user = {}
    try:
        user_id = request.args.get('id')
        print(user_id)
        user = getUserDB(user_id)
    except:
        print("Error accessing the User DataBase.")
    return jsonify(user)

#Incrementing the number of views on the user "id"
@app.route('/user/view/add/', methods=["PUT"])
def addNewView():
    user_id = request.args.get('id')

    try:
        return {"views": newView(user_id)}
    except:
        print("Error in addNewView.")
        return jsonify()

#Incrementing the number of videos posted by user "id"
@app.route('/user/video/add/', methods=["PUT"])
def addNewVideo():
    user_id = request.args.get('id')

    try:
        return {"videos": newVideo(user_id)}
    except:
        print("Error in addNewVideo.")
        return jsonify()

#Incrementing the number of questions posted by user "id"
@app.route('/user/question/add/', methods=["PUT"])
def addNewQuestion():
    user_id = request.args.get('id')

    try:
        return {"questions": newQuestion(user_id)}
    except:
        print("Error in addNewQuestion.")
        return jsonify()

#Incrementing the number of answers posted by user "id"
@app.route('/user/answer/add/', methods=["PUT"])
def addNewAnswer():
    user_id = request.args.get('id')

    try:
        return {"answers": newAnswer(user_id)}
    except:
        print("Error in addNewAnswer.")
        return jsonify()

#Listing of all user events (all entries of the User Table)
@app.route('/users/get', methods=["GET"])
def getListUsers():
    users = {}
    try:
        users = listUsersDict()
    except:
        print("Error in getListUsers.")
    return jsonify(users)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4700, debug=True)
