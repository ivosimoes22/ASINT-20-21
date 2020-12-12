from flask import Flask
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify, url_for
from flask import session
import requests

#from user_manager import *

#necessary so that our server does not need https
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



components = {
    'user_manager': "http://127.0.0.1:4700/",
    'video_db': "http://127.0.0.1:4800/",
    'qa': "http://127.0.0.1:4900/"
}


app = Flask(__name__)
app.secret_key = "secretkey"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
fenix_blueprint = OAuth2ConsumerBlueprint(
    "fenix-example", __name__,
    client_id="1695915081466090",
    client_secret="4PBXvlpFFmdJqwQHgvZIz83piDpT15pc5uyyJn0GYiAAUUeVWhquCAz+y9jwBXo0geKUT4jXmqc9ztJ9PmeU9A==",
    base_url="https://fenix.tecnico.ulisboa.pt/",
    token_url="https://fenix.tecnico.ulisboa.pt/oauth/access_token",
    authorization_url="https://fenix.tecnico.ulisboa.pt/oauth/userdialog",
)
app.register_blueprint(fenix_blueprint)

loggedUsers = {}

#User Authentication
@app.route('/')
def home_page():
    # verification if the user is logged in
    try:
        if fenix_blueprint.session.authorized != False:
            resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
            user_data = resp.json()
            userInfo = {}
            userInfo["id"] = user_data["username"]
            userInfo["name"] = user_data["name"]
            url = components["user_manager"] + 'addUser'
            msg = requests.post(url=url, data=userInfo)

            if msg.status_code != 200:
                print('Error in posting on User Manager!')
        
            return render_template("listVideos.html")
    except:
        print("Session Expired")
    return render_template("welcomePage.html")


#User Authentication
@app.route('/auth')
def authFunction():
    return redirect(url_for("fenix-example.login"))

@app.route('/logout')
def logout():
    # this clears all server information about the access token of this connection
    session.clear()
    return redirect(url_for("home_page"))
  
@app.route('/video_page/<int:id>')
def getVideoPage(id):
    return render_template("videoPage.html")


#API
@app.route('/api/videos/', methods=['POST'])
def addNewVideo():
    if fenix_blueprint.session.authorized == True:
        videoInfo = {}
        try:
            videoInfo = request.get_json()
            #Get the ID of the user creating the video
            resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
            videoInfo["userId"] = resp.json()["username"]
            url = components["video_db"] + 'addVideo'
            msg = requests.post(url=url, data=videoInfo)

            if msg.status_code != 200:
                print('Error in posting on VideoDB!')
        except:
            print("Error receiving video info!")
        return jsonify()
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/videos/", methods=['GET'])
def getListOfVideos():
    if fenix_blueprint.session.authorized == True:
        url = components["video_db"]+'getVideos'
        videosDict = requests.get(url=url)
        return {"videos": videosDict.json()}
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/getVideo/<int:id>", methods=["GET"])
def getSingleVideo(id):
    print(id)
    if fenix_blueprint.session.authorized == True:
        url = components["video_db"]+'getVideo/'+str(id)
        videoDict = requests.get(url=url)
        return jsonify(videoDict.json())
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/videos/<int:id>/question", methods=["GET"])
def getListOfQuestions(id):
    if fenix_blueprint.session.authorized == True:
        questions = {}
        url = components["qa"]+'/video/'+str(id)+'/getQuestions'
        try:
            questions = requests.get(url=url)
        except:
            print("Error getting")
        return {"questions": questions.json()}
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/addQuestion/", methods=["POST"])
def addNewQuestion():
    if fenix_blueprint.session.authorized == True:
        question = {}
        try:
            question = request.get_json()
            print(question)
            #Get the ID of the user creating the video
            resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
            question["userId"] = resp.json()["username"]
            url = components["qa"] + 'addQuestion'
            msg = requests.post(url=url, data=question)
        except:
            print("Error receiving question info")
        return jsonify()
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/getQuestion/<int:id>", methods=["GET"])
def getSingleQuestion(id):
    if fenix_blueprint.session.authorized == True:
        url = components["qa"]+'getQuestion/'+str(id)
        question = requests.get(url=url)
        return jsonify(question.json())
    else:
        redirect(url_for("fenix-example.login"))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)