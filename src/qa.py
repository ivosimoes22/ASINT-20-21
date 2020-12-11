from time import time
import requests
from requests.sessions import Request
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Time, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import query_expression, relationship, scoped_session

from sqlalchemy.orm import sessionmaker
from os import abort, path, times

from flask import Flask
from flask import jsonify
from flask import request
from sqlalchemy.sql.sqltypes import Float, Time

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
    timestamp = Column(Float)

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

#Functions related with Question Class
def listQuestions(video_id):
    return db_session.query(Question).filter(Question.video_id==video_id).order_by(Question.timestamp)

def listQuestionsDict(video_id):
    questions = []
    questionList = listQuestions(video_id)
    for question in questionList:
        q = question.to_dict()
        questions.append(q)
    return questions

def getNumberOfQuestions(video_id):
    return db_session.query(Question).filter(Question.video_id==video_id).count()

def addNewQuestionDB(questionBody, videoId, user_id, timestamp):
    newQuestion = Question(q_text=questionBody, video_id=videoId, user_id=user_id, timestamp=float(timestamp))

    try:
        db_session.add(newQuestion)
        db_session.commit()
        return newQuestion.id
    except:
        db_session.rollback()
        return None


#Endpoint functions
@app.route('/video/<int:id>/getQuestions', methods=["GET"])
def returnNumberQuestions(id):
    questions = {}
    try:
        questions = listQuestionsDict(id)
    except:
        print("Error in get")
    return jsonify(questions)


@app.route('/addQuestion', methods=["POST"])
def addNewQuestion():
    try:
        if addNewQuestionDB(request.form["text"], request.form["video_id"], request.form["userId"], request.form["timestamp"]) is not None:
            print("New question added to DB")
        else:
            print("Couldnt add question")
    except:
        print("Error adding to QuestionDB")
    return jsonify()


# @app.route('/getQuestions', methods=["POST"])
# def getListQuestions

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4900, debug=True)