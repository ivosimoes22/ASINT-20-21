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

adminUsers = {"user_id": ["ist187024"]}


def getCurrentUser():
    resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
    user_data = resp.json()
    return user_data


#User Authentication
@app.route('/')
def home_page():
    # verification if the user is logged in
    try:
        if fenix_blueprint.session.authorized != False:
            user_data = getCurrentUser()
            userInfo = {}
            userInfo["id"] = user_data["username"]
            userInfo["name"] = user_data["name"]
            url = components["user_manager"] + 'user/add'

            try:
                msg = requests.post(url=url, data=userInfo)
            except:
                print("Error in POST")

            if user_data["username"] in adminUsers["user_id"]:
                print("You are an ADMIN")
                return render_template("listVideos.html", isAdmin=True)
        
            return render_template("listVideos.html", isAdmin=False)
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


#Sends the user to the video Page  
@app.route('/video_page/<int:id>')
def getVideoPage(id):
    if fenix_blueprint.session.authorized == False:
        return render_template("welcomePage.html")
    else:
         return render_template("videoPage.html")


#API
@app.route('/api/video/add', methods=['POST'])
def addNewVideo():
    if fenix_blueprint.session.authorized == True:
        videoInfo = {}
        try:
            videoInfo = request.get_json()
            videoInfo["userId"] = getCurrentUser()["username"]
            url = components["video_db"] + 'video/add'
            msg = requests.post(url=url, data=videoInfo)

        except:
            print("Error receiving video info!")

        #add a video to the user DB
        url = components["user_manager"]+'user/video/add/?id='+getCurrentUser()["username"]

        try:
            user_resp = requests.put(url=url)
        except:
            print("Error in put")

        return jsonify()
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/video/get", methods=['GET'])
def getListOfVideos():
    if fenix_blueprint.session.authorized == True:
        url = components["video_db"]+'video/get'
        videosDict = requests.get(url=url)
        return {"videos": videosDict.json()}
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/video/<int:id>/get", methods=["GET"])
def getSingleVideo(id):
    if fenix_blueprint.session.authorized == True:
        url = components["video_db"]+'video/'+str(id)+'/get'
        videoDict = requests.get(url=url)
        return jsonify(videoDict.json())
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/video/<int:id>/question/get", methods=["GET"])
def getListOfQuestions(id):
    if fenix_blueprint.session.authorized == True:
        questions = {}
        url = components["qa"]+'/video/'+str(id)+'/question/get'
        try:
            questions = requests.get(url=url)
        except:
            print("Error getting")
        return {"questions": questions.json()}
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/question/add", methods=["POST"])
def addNewQuestion():
    if fenix_blueprint.session.authorized == True:
        question = {}
        try:
            question = request.get_json()
            print(question)
            #Get the ID of the user creating the video
            question["userId"] = getCurrentUser()["username"]
            url = components["qa"] + 'question/add'
            msg = requests.post(url=url, data=question)
        except:
            print("Error receiving question info")

        #add a question to the user DB
        url = components["user_manager"]+'user/question/add/?id='+getCurrentUser()["username"]

        try:
            user_resp = requests.put(url=url)
        except:
            print("Error in put")

        
        return jsonify()
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/question/<int:id>/get", methods=["GET"])
def getSingleQuestion(id):
    if fenix_blueprint.session.authorized == True:
        url = components["qa"]+'question/'+str(id)+'/get'
        question = requests.get(url=url)
        return jsonify(question.json())
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/user/get/", methods=["GET"])
def getUser():
    if fenix_blueprint.session.authorized == True:
        user_id = request.args.get('id')
        print(user_id)
        url = components["user_manager"]+'user/get/?id='+user_id
        user = requests.get(url=url)
        return jsonify(user.json())
    else:
        redirect(url_for("fenix-example.login"))

@app.route("/api/answer/add", methods=["POST"])
def addNewAnswer():
    if fenix_blueprint.session.authorized == True:
        answer = {}
        try:
            answer = request.get_json()
            answer["userId"] = getCurrentUser()["username"]
            url = components["qa"] + 'answer/add'
            msg = requests.post(url=url, data=answer)
        except:
            print("Error")

        #add an answer to the user DB
        url = components["user_manager"]+'user/answer/add/?id='+getCurrentUser()["username"]

        try:
            user_resp = requests.put(url=url)
        except:
            print("Error in put")

        
    return jsonify()


@app.route("/api/answer/<int:q_id>/get", methods=["GET"])
def getListOfAnswers(q_id):
    if fenix_blueprint.session.authorized == True:
        answers = {}
        url = components["qa"]+'/answer/'+str(q_id)+'/get'
        try:
            answers = requests.get(url=url)
        except:
            print("Error getting")
        return {"answers": answers.json()}
    else:
        return jsonify()


@app.route("/api/video/view/<int:id>/add", methods=["PUT"])
def addVideoView(id):
    if fenix_blueprint.session.authorized == True:
        resp = {}
        url = components["video_db"]+'video/view/'+str(id)+'/add'
        try:
            resp = requests.put(url=url)
        except:
            print("Error in put")

        #Increase the view also for the user
        url = components["user_manager"]+'user/view/add/?id='+getCurrentUser()["username"]

        try:
            user_resp = requests.put(url=url)
        except:
            print("Error in put")

        return jsonify(resp.json())
    else:
        return jsonify()

##Admin Pages##
@app.route('/admin/user_stats')
def getUserStats():
    if fenix_blueprint.session.authorized == False:
        return render_template("welcomePage.html")
    else:
        if getCurrentUser()["username"] in adminUsers["user_id"]:
            return render_template("userStats.html")
        else:
            return redirect(url_for("home_page"))

##Admin API##
@app.route('/admin/api/users/get', methods=["GET"])
def getListOfUsers():
    if fenix_blueprint.session.authorized == True and getCurrentUser()["username"] in adminUsers["user_id"]:
        users = {}
        url = components["user_manager"]+'users/get'
        try:
            users = requests.get(url=url)
        except:
            print("Error getting")
        return {"users": users.json()}
    else:
        return jsonify()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)