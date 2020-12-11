from enum import unique
import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session

from sqlalchemy.orm import sessionmaker
from os import abort, path

from flask import Flask
from flask import jsonify
from flask import request

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
    description = Column(String)
    views = Column(Integer, default = 0)
    userId = Column(String)

    def __repr__(self):
        return "<Video (Id=%d, URL=%s, Title=%s, Description=%s, Views=%d, User=%s>)" % (self.id, self.url, self.title, self.description, self.views, self.userId)

    def to_dict(self):
        return {'video_id': self.id, 'url': self.url, 'title': self.title, 'description': self.description, 'views': self.views, 'userId': self.userId}


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


def addNewVideoDB(url, title, description, userId):
    newVideo = Video(url=url, title=title, description=description, userId=userId)

    try:
        db_session.add(newVideo)
        db_session.commit()
        return newVideo.url
    except:
        db_session.rollback()
        return None

def returnSingleVideoDB(id):
    video = db_session.query(Video).filter(Video.id==id).first()    
    videoDict = video.to_dict()
    return videoDict


@app.route('/addVideo', methods=['POST'])
def addNewVideo():
    if request.method == "POST":
        try:
            print(request.form["url"])
            if addNewVideoDB(request.form["url"], request.form["title"], request.form["description"], request.form["userId"]) is not None:
                print("New Video added with success")
            else:
                print("Couldnt add video")
        except:
            print("Error addding to VideoDB")
        
        print(listVideosDict())
        return jsonify()


@app.route('/getVideos', methods=['GET'])
def getListVideos():
    try:
        videos = listVideosDict()
    except:
        abort(404)
    return jsonify(videos)

@app.route('/getVideo/<int:id>', methods=["GET"])
def returnSingleVideo(id):
    video = {}
    try:
        video = returnSingleVideoDB(id)
        print(video)
    except:
        print("Error")
    return jsonify(video)
        

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4800, debug=True)