import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from os import path
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

#SLQ access layer initialization
DATABASE_FILE = "db_logs.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of the Message Table
class MessageEvent(Base):
    __tablename__ = 'MessageEvent'
    id = Column(Integer, primary_key=True)
    timestamp = Column(String,nullable=False)
    request = Column(String)

    def __repr__(self):
        return "<MessageEvent (Id=%d, TimeStamp=%s, Request=%s>)" % (self.id, self.timestamp, self.request)

    def to_dict(self):
        return {'msg_id': self.id, 'timestamp': self.timestamp, 'request': self.request}

#Declaration of the Data Table
class DataEvent(Base):
    __tablename__ = 'DataEvent'
    id = Column(Integer, primary_key=True)
    timestamp = Column(String,nullable=False)
    d_type = Column(String)
    d_content = Column(String)
    user = Column(String,ForeignKey('User.id'))

    def __repr__(self):
        return "<DataEvent (Id=%d, TimeStamp=%s, Type=%s, Content=%s, User=%s>)" % (self.id, self.timestamp, self.d_type, self.d_content, self.user)

    def to_dict(self):
        return {'data_id': self.id, 'timestamp': self.timestamp, 'd_type': self.d_type, 'd_content': self.d_content, 'user': self.user}


Base.metadata.create_all(engine) #Create tables for the data models
db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)


#Functions related with the Message DataBase

#Listing of all message events
def listMessagesEvents():
    return db_session.query(MessageEvent).order_by(MessageEvent.timestamp).all()

#Listing of message events to dictionary
def listMessagesEventsDict():
    logs = []
    logList = listMessagesEvents()
    for log in logList:
        l = log.to_dict()
        logs.append(l)
    return logs

#Adding the new message event to the Message Table
def addMessageEventDB(timestamp, msg):
    newMsg = MessageEvent(timestamp=timestamp, request=msg)

    try:
        db_session.add(newMsg)
        db_session.commit()
        return newMsg.id
    except:
        db_session.rollback()
        return None


#Functions related with the Data DataBase

#Listing of all data events
def listDataEvents():
    return db_session.query(DataEvent).order_by(DataEvent.timestamp).all()

#Listing of data events to dictionary
def listDataEventsDict():
    logs = []
    logList = listDataEvents()
    for log in logList:
        l = log.to_dict()
        logs.append(l)
    return logs

#Adding the new data event to the Data Table
def addDataEventDB(timestamp, d_type, d_content, user):
    newData = DataEvent(timestamp=timestamp, d_type=d_type, d_content=d_content, user=user)

    try:
        db_session.add(newData)
        db_session.commit()
        return newData.id
    except:
        db_session.rollback()
        return None


#Endpoint functions

#Posting new message (Message Creation Events)
@app.route('/store/message_events', methods=["POST"])
def addNewMessageEvent():
    try:
        #print(request.form["request"])
        if addMessageEventDB(str(request.form["timestamp"]), str(request.form["request"])) is not None:
            print("New message added with success.")
        else:
            print("Couldn't add the message.")
    except:
        print("Error addding to MessageEventDB.")

    #print(listMessagesEventsDict())
    return jsonify()

#Listing of all message events (all entries of the message table)
@app.route('/message_events/get', methods=["GET"])
def getMessageEvents():
    msgs = {}
    try:
        msgs = listMessagesEventsDict()
    except:
        print("Error listing message events")
    return jsonify(msgs)


#Posting new data (Data Creation Events)
@app.route('/store/data_events', methods=["POST"])
def addNewDataEvent():
    try:
        #print(request.form["request"])
        if addDataEventDB(request.form["timestamp"], request.form["d_type"], request.form["d_content"], request.form["user"]) is not None:
            print("New data added with success.")
        else:
            print("Couldn't add the data.")
    except:
        print("Error addding to DataEventDB.")

    print(listDataEventsDict())
    return jsonify()

#Listing of all data events (all entries of the data table)
@app.route('/data_events/get', methods=["GET"])
def getDataCreationEvents():
    data = {}
    try:
        data = listDataEventsDict()
    except:
        print("Error listing data events")
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, port=4600)
