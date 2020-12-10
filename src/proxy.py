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
    'user_manager': "http://127.0.0.1:4700/"
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
    if fenix_blueprint.session.authorized != False:
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        user_data = resp.json()
        
        #Keep track of users logged in    ##Not sure yet if needed
        #loggedUsers[user_data["username"]] = user_data["name"]

        userInfo = {}
        userInfo["id"] = user_data["name"]
        userInfo["name"] = user_data["name"]
        url = components["user_manager"] + 'addUser'
        msg = requests.post(url=url, data=userInfo)

        if msg.status_code != 200:
            print('Error in posting on User Manager!')
     
        return render_template("listVideos.html")
        #print(loggedUsers)

    #return app.send_static_file('welcomepage.html')
    return render_template("welcomePage.html")


#User Authentication
@app.route('/auth')
def authFunction():
    return redirect(url_for("fenix-example.login"))

@app.route('/logout')
def logout():
    # this clears all server information about the access token of this connection
    res = str(session.items())
    print(res)
    session.clear()
    res = str(session.items())
    print(res)
    return redirect(url_for("home_page"))
  

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




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)