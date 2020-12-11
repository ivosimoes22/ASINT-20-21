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
            print(user_data)
            #Keep track of users logged in    ##Not sure yet if needed
            #loggedUsers[user_data["username"]] = user_data["name"]

            userInfo = {}
            userInfo["id"] = user_data["username"]
            userInfo["name"] = user_data["name"]
            url = components["user_manager"] + 'addUser'
            msg = requests.post(url=url, data=userInfo)

            if msg.status_code != 200:
                print('Error in posting on User Manager!')
        
            return render_template("listVideos.html")
            #print(loggedUsers)

        #return app.send_static_file('welcomepage.html')
        return render_template("welcomePage.html")
    except:
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

@app.route('/private')
def private_page():
    #this page can only be accessed by a authenticated user

    # verification of the user is  logged in
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #res contains the responde made to /api/fenix/vi/person (information about current user)
        user_data = resp.json()

        return render_template("privPage.html", username=user_data['username'], name=user_data['name'])

#API
@app.route('/api/videos/', methods=['POST'])
def createNewVideo():
    if fenix_blueprint.session.authorized == True:
        if request.method == "POST":
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
def returnsVideosJSON():
    if fenix_blueprint.session.authorized == True:
        if request.method == "GET":
            videosDict = requests.get(components["video_db"]+'getVideos')
            return {"videos": videosDict.json()}
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/getVideo/<int:id>", methods=["GET"])
def returnSingleVideo(id):
    print(id)
    if fenix_blueprint.session.authorized == True:
        if request.method == "GET":
            url = components["video_db"]+'getVideo/'+str(id)
            videoDict = requests.get(url=url)
            return jsonify(videoDict.json())
    else:
        redirect(url_for("fenix-example.login"))


@app.route("/api/videos/<int:id>/question", methods=["GET"])
def returnNumeberOfQuestions(id):
    if fenix_blueprint.session.authorized == True:
        nr_question = {}
        if request.method == "GET":
            url = components["qa"]+'/video/'+str(id)+'/questions/number'
            try:
                nr_question = requests.get(url=url)
            except:
                print("Error getting")
            return jsonify(nr_question.json())
    else:
        redirect(url_for("fenix-example.login"))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)