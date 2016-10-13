from flask import Flask
from flask import request
from flask import abort
import hmac
import main
import hashlib

app = Flask(__name__)


def verifySecret(signature,body):
    mac = hmac.new(bytes(main.readSecret("auth.conf"), 'utf-8'), msg=body, digestmod=hashlib.sha1)

    if not str(mac.hexdigest()) == signature:
        print(mac.hexdigest()+" vs. "+signature)
        abort(403)

@app.route('/hook', methods=['POST'])
def hook():
    data = request.get_json()

    # get only the signature from signature head in HTTP request
    signature = request.headers['X-Hub-Signature']
    print(signature)
    body = request.data
    verifySecret(signature,body)

    token, username = main.readConfig("auth.conf")
    session = main.createSession(token)
    # read all rules
    content = main.readRules("rules.conf")
    main.labelIssues(session, "MI-PYT-TestRepo", username,
                     "default", False,
                     2, content)

    return ''


@app.route('/')
def hello():
    return 'Set your github webhook to URL /hook and it will process new issues.'

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)