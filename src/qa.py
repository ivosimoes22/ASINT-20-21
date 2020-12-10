import requests
from requests.sessions import Request
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import query_expression, relationship, scoped_session

from sqlalchemy.orm import sessionmaker
from os import abort, path

from flask import Flask
from flask import jsonify
from flask import request
from sqlalchemy.sql.sqltypes import Time

app = Flask(__name__)

#SLQ access layer initialization
DATABASE_FILE = "db_qa.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

class Question(Base):
    __tablename__= 'Question'
    id = Column(Integer, primary_key=True)
    q_text = Column(String)
    video_id = Column(Integer)
    user_id = Column(String)
    timestamp = Column(Time)

    def __repr__(self):
        return "<Question (Id=%d, Text=%s, VideoId=%d, UserId=%s, Timestamp=%s)" %  (self.id, self.q_text, self.video_id, self.user_id, self.timestamp)

    def to_dict(self):
        return {'q_id': self.id, 'q_text': self.q_text, 'video_id': self.video_id, 'user_id': self.user_id, 'timestamp': self.timestamp}


class Answer(Base):
    __tablename__ = 'Answer'
    id = Column(Integer, primary_key=True)
    a_text = Column(String)
    video_id = Column(Integer)
    user_id = Column(String)
    q_id = Column(Integer)
    def __repr__(self):
        return "<Answer (Id=%d, Text=%s, VideoId=%d, UserId=%s, QuestionId=%s)" %  (self.id, self.a_text, self.video_id, self.user_id, self.q_id)

    def to_dict(self):
        return {'q_id': self.id, 'a_text': self.a_text, 'video_id': self.video_id, 'user_id': self.user_id, 'q_id': self.q_id}


Base.metadata.create_all(engine) #Create tables for the data models
db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)

def listQuestions():
    return db_session.query(Question).all()

def listQuestionsDict():
    questions = []
    questionList = listQuestions()
    for question in questionList:
        q = question.to_dict()
        questions.append(q)
    return questions

def getNumberOfQuestions(video_id):
    return db_session.query(Question).filter(Question.video_id==video_id).count()


@app.route('/video/<int:id>/questions/number', methods=["GET"])
def returnNumberQuestions(id):
    nr_questions = {}
    if request.method == "GET":
        try:
            nr_questions["nr_questions"] = getNumberOfQuestions(id)
        except:
            print("Error in get")
    return jsonify(nr_questions)   


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4900, debug=True)