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
        return {'a_id': self.id, 'a_text': self.a_text, 'video_id': self.video_id, 'user_id': self.user_id, 'q_id': self.q_id}


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

def getSingleQuestionDB(q_id):
    q = db_session.query(Question).filter(Question.id==q_id).first()
    q_dict = q.to_dict()
    return q_dict

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

#Functions related with Answer Class
def listAns():
    return db_session.query(Answer).all()

def listAnswers(q_id):
    return db_session.query(Answer).filter(Answer.q_id==q_id)

def listAnswersDict(q_id):
    answers = []
    answerList = listAnswers(q_id)
    for answer in answerList:
        a = answer.to_dict()
        answers.append(a)
    return answers

def addNewAnswerDB(answerBody, videoId, user_id, q_id):
    newAnswer = Answer(a_text=answerBody, video_id=videoId, user_id=user_id, q_id=q_id)

    try:
        db_session.add(newAnswer)
        db_session.commit()
        return newAnswer.id
    except:
        db_session.rollback()
        return None


#Endpoint functions
@app.route('/video/<int:id>/question/get', methods=["GET"])
def getQuestions(id):
    questions = {}
    try:
        questions = listQuestionsDict(id)
    except:
        print("Error in get")
    return jsonify(questions)


@app.route('/question/add', methods=["POST"])
def addNewQuestion():
    try:
        if addNewQuestionDB(request.form["text"], request.form["video_id"], request.form["userId"], request.form["timestamp"]) is not None:
            print("New question added to DB")
        else:
            print("Couldnt add question")
    except:
        print("Error adding to QuestionDB")
    return jsonify()


@app.route('/question/<int:id>/get', methods=["GET"])
def getSingleQuestion(id):
    question = {}
    try:
        question = getSingleQuestionDB(id)
    except:
        print("Error getting question from DB")
    return jsonify(question)


@app.route('/answer/add', methods=["POST"])
def addNewAnswer():
    try:
        if addNewAnswerDB(request.form["a_text"], request.form["video_id"], request.form["userId"], request.form["q_id"]) is not None:
            print("New answer added to DB")
        else:
            print("Couldnt add answer")
    except:
        print("Error adding to AnswerDB")
    print(listAns())
    return jsonify()


@app.route('/answer/<int:q_id>/get', methods=["GET"])
def getAnswers(q_id):
    answers = {}
    try:
        answers = listAnswersDict(q_id)
    except:
        print("Error in get")
    return jsonify(answers)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4900, debug=True)