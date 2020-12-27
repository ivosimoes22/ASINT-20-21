import requests
from requests.sessions import Request
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from os import path
from flask import Flask
from flask import jsonify
from flask import request
from sqlalchemy.sql.sqltypes import Float
from datetime import datetime


logs = "http://127.0.0.1:4600/"

app = Flask(__name__)

#SLQ access layer initialization
DATABASE_FILE = "db_qa.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of the Question Table
class Question(Base):
    __tablename__= 'Question'
    id = Column(Integer, primary_key=True)
    q_text = Column(String,nullable=False)
    video_id = Column(Integer,ForeignKey('Video.id'))
    user_id = Column(String,ForeignKey('User.id'))
    timestamp = Column(Float,nullable=False)

    def __repr__(self):
        return "<Question (Id=%d, Text=%s, VideoId=%d, UserId=%s, Timestamp=%s)" %  (self.id, self.q_text, self.video_id, self.user_id, self.timestamp)

    def to_dict(self):
        return {'q_id': self.id, 'q_text': self.q_text, 'video_id': self.video_id, 'user_id': self.user_id, 'timestamp': self.timestamp}

#Declaration of the Answer Table
class Answer(Base):
    __tablename__ = 'Answer'
    id = Column(Integer, primary_key=True)
    a_text = Column(String,nullable=False)
    video_id = Column(Integer,ForeignKey('Video.id'))
    user_id = Column(String,ForeignKey('User.id'))
    q_id = Column(Integer,ForeignKey('Question.id'))

    def __repr__(self):
        return "<Answer (Id=%d, Text=%s, VideoId=%d, UserId=%s, QuestionId=%s)" %  (self.id, self.a_text, self.video_id, self.user_id, self.q_id)

    def to_dict(self):
        return {'a_id': self.id, 'a_text': self.a_text, 'video_id': self.video_id, 'user_id': self.user_id, 'q_id': self.q_id}


Base.metadata.create_all(engine) #Create tables for the data models
db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)


#Functions related with Question Class

#Listing of all question events
def listQuestions(video_id):
    return db_session.query(Question).filter(Question.video_id==video_id).order_by(Question.timestamp)

#Listing of question events to dictionary
def listQuestionsDict(video_id):
    questions = []
    questionList = listQuestions(video_id)
    for question in questionList:
        q = question.to_dict()
        questions.append(q)
    return questions

#Querying the Question Table to find a specific question corresponding to "id"
def getSingleQuestionDB(q_id):
    q = db_session.query(Question).filter(Question.id==q_id).first()
    q_dict = q.to_dict()
    return q_dict

#Querying the Question Table to find the total number of questions
def getNumberOfQuestions(video_id):
    return db_session.query(Question).filter(Question.video_id==video_id).count()

#Adding the new question event to the Question Table
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

#Listing of all answer events
def listAns():
    return db_session.query(Answer).all()

#Querying the Answer Table to find a specific answer corresponding to "id"
def listAnswers(q_id):
    return db_session.query(Answer).filter(Answer.q_id==q_id)

#Listing of answer events to dictionary
def listAnswersDict(q_id):
    answers = []
    answerList = listAnswers(q_id)
    for answer in answerList:
        a = answer.to_dict()
        answers.append(a)
    return answers

#Adding the new answer event to the Answer Table
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

@app.before_request
def beforeRequest():
    log = {}
    log["timestamp"] = str(datetime.now())
    log["request"] = str(request.url) + ' [' + str(request.method) + ']'
    url = logs+'store/message_events'

    try:
        resp = requests.post(url=url, data=log)
    except:
        print("Error in beforeRequest.")
    return

#Listing of all question events (all entries of the Question Table)
@app.route('/video/<int:id>/question/get', methods=["GET"])
def getQuestions(id):
    questions = {}
    try:
        questions = listQuestionsDict(id)
    except:
        print("Error in GET.")
    return jsonify(questions)

#Adding a new question (Question Creation Events)
@app.route('/question/add', methods=["POST"])
def addNewQuestion():
    try:
        qid = addNewQuestionDB(request.form["text"], request.form["video_id"], request.form["userId"], request.form["timestamp"])
        if qid is not None:
            print("New question addeded successfully.")

            #Add data creation Log
            data = {"timestamp": str(datetime.now()), "d_type": "Question", "user": request.form["userId"]}
            data["d_content"] = 'QuestionID: ' + str(qid) + '; Body: ' + request.form["text"] + '; VideoID: ' + str(request.form["video_id"]) + '; Timestamp: ' + str(request.form["timestamp"])

            try:
                resp = requests.post(url=logs+'store/data_events', data=data)
            except:
                print("Error in POST.")

        else:
            print("Couldn't add the question.")
    except:
        print("Error in POST to Question DataBase.")
    return jsonify()

#Querying the Question Table for a specific "id"
@app.route('/question/<int:id>/get', methods=["GET"])
def getSingleQuestion(id):
    question = {}
    try:
        question = getSingleQuestionDB(id)
    except:
        print("Error getting question from DataBase.")
    return jsonify(question)

#Adding a new answer (Answer Creation Events)
@app.route('/answer/add', methods=["POST"])
def addNewAnswer():
    try:
        aid = addNewAnswerDB(request.form["a_text"], request.form["video_id"], request.form["userId"], request.form["q_id"])
        if aid is not None:
            print("New answer addeded successfully.")

            #Add data creation Log
            data = {"timestamp": str(datetime.now()), "d_type": "Answer", "user": request.form["userId"]}
            data["d_content"] = 'AnswerID: ' + str(aid) + '; Body: ' + request.form["a_text"] + '; VideoID: ' + str(request.form["video_id"]) + '; QuestionID: ' + str(request.form["q_id"])

            try:
                resp = requests.post(url=logs+'store/data_events', data=data)
            except:
                print("Error in POST answer.")

        else:
            print("Couldn't add the answer.")
    except:
        print("Error adding answer to Answer DataBase.")
    print(listAns())
    return jsonify()

#Listing of all answer events to a specific question (all entries of the Answer Table corresponding to "q_id")
@app.route('/answer/<int:q_id>/get', methods=["GET"])
def getAnswers(q_id):
    answers = {}
    try:
        answers = listAnswersDict(q_id)
    except:
        print("Error in GET answers.")
    return jsonify(answers)

#Running Locally
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4900, debug=True)
