from . import issuelabel
from flask import Flask
from flask import request
from flask import abort
import hmac
import hashlib
from flask import render_template

app = Flask(__name__)


def verifySecret(signature, body):
    """
    This function will calculate SHA1 HMAC from secret and message body.
    Secret is parsed from auth configuration file.

    HMAC is then compared to a signature which was delivered in header of HTTP request.
    If signature is correct, this tool will process HTTP request,
    if signature is not correct HTTP error code 403 (Forbidden) is returned.


    :param string signature: Signature from HTTP header.

    :param string body: Content of HTTP POST request.
    """
    # create hmac
    mac = hmac.new(bytes(issuelabel.readSecret("auth.conf"), 'utf-8'),
                   msg=body, digestmod=hashlib.sha1)

    # if signature and calculated hash doesnt match, abort with error code 403
    if not str(mac.hexdigest()) == signature:
        abort(403)


@app.route('/hook', methods=['POST'])
def hook():
    """
    This function checks /hook route. It is used for processing incoming HTTP POST request from GitHub.

    :return: Empty string as response.
    """
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

    if data["action"] == "opened":
        issuelabel.labelIssues(session, repoName, username,
                         "default", False, 0,
                         content, data["issue"])

    return ''


@app.route('/')
def hello():
    """
    This function fill render template index.html. This template is used on default route /. It also works as simple README.

    :return:

    Rendered HTML file.
    """
    return render_template('index.html')

def run():
    """
    This function will run web mode of the tool.
    """
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
