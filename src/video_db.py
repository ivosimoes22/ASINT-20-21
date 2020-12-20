import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import scoped_session
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from os import abort, path
from flask import Flask
from flask import jsonify
from flask import request
import json

logs = "http://127.0.0.1:4600/"

app = Flask(__name__)

#SLQ access layer initialization
DATABASE_FILE = "db_videos.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

class Video(Base):
    __tablename__ = 'Video'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    title = Column(String)
    views = Column(Integer, default = 0)
    userId = Column(String)

    def __repr__(self):
        return "<Video (Id=%d, URL=%s, Title=%s, Views=%d, User=%s>)" % (self.id, self.url, self.title, self.views, self.userId)

    def to_dict(self):
        return {'video_id': self.id, 'url': self.url, 'title': self.title, 'views': self.views, 'userId': self.userId}


Base.metadata.create_all(engine) #Create tables for the data models
db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)

def listVideos():
    return db_session.query(Video).all()

def listVideosDict():
    videos = []
    videoList = listVideos()
    for video in videoList:
        v = video.to_dict()
        videos.append(v)
    return videos


def addNewVideoDB(url, title, userId):
    newVideo = Video(url=url, title=title, userId=userId)

    try:
        db_session.add(newVideo)
        db_session.commit()
        return newVideo.id
    except:
        db_session.rollback()
        return None

def getSingleVideoDB(id):
    video = db_session.query(Video).filter(Video.id==id).first()    
    videoDict = video.to_dict()
    return videoDict

def newView(id):
    v = db_session.query(Video).filter(Video.id==id).first()
    v.views+=1
    n_view = v.views
    db_session.commit()
    db_session.close()
    print(listVideosDict())
    return n_view

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


@app.route('/video/add', methods=['POST'])
def addNewVideo():
    try:
        print(request.form["url"])
        vid = addNewVideoDB(request.form["url"], request.form["title"], request.form["userId"])
        if vid is not None:
            print("New Video added with success")

            #Add data creation Log
            data = {"timestamp": str(datetime.now()), "d_type": "Video", "user": request.form["userId"]}
            data["d_content"] = 'VideoID: ' + str(vid) + '; Url: ' + request.form["url"] + '; Title: ' + request.form["title"]
            try:
                resp = requests.post(url=logs+'store/data_events', data=data)
            except:
                print("Error in POST")


        else:
            print("Couldnt add video")
    except:
        print("Error addding to VideoDB")
    
    #print(listVideosDict())
    return jsonify()


@app.route('/video/get', methods=['GET'])
def getListVideos():
    try:
        videos = listVideosDict()
    except:
        abort(404)
    return jsonify(videos)


@app.route('/video/<int:id>/get', methods=["GET"])
def getSingleVideo(id):
    video = {}
    try:
        video = getSingleVideoDB(id)
        print(video)
    except:
        print("Error")
    return jsonify(video)


@app.route('/video/view/<int:id>/add', methods=["PUT"])
def addNewView(id):
    try:
        return {"id": id, "views": newView(id)}
    except:
        print("Error")
        return jsonify()

        

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4800, debug=True)