from . import issuelabel
from flask import Flask
from flask import request
from flask import abort
import hmac
#from .issuelabel import readSecret, readConfig, createSession, readRules, labelIssues
import hashlib
from flask import render_template

app = Flask(__name__)


def verifySecret(signature, body):
    # create hash
    mac = hmac.new(bytes(issuelabel.readSecret("auth.conf"), 'utf-8'),
                   msg=body, digestmod=hashlib.sha1)

    # if signature and calculated hash doesnt match, abort with error code 403
    if not str(mac.hexdigest()) == signature:
        abort(403)


@app.route('/hook', methods=['POST'])
def hook():
    data = request.get_json()

    # get only the signature from signature head in HTTP request
    signature = request.headers['X-Hub-Signature'].split("=")[1]

    body = request.data
    # compare signature and calculated hash from body
    verifySecret(signature, body)

    token, username = issuelabel.readConfig("auth.conf")
    session = issuelabel.createSession(token)

    # read all rules
    content = issuelabel.readRules("rules.conf")

    # get name of repository
    repoName = data["repository"]["name"]
    print(repoName)
    if data["action"] == "opened":
        issuelabel.labelIssues(session, repoName, username,
                         "default", False, 0,
                         content, data["issue"])

    return ''


@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
