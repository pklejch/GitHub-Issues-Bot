[![Build Status](https://travis-ci.com/pklejch/GitHub-Issues-Bot.svg?token=Wsjf89ecpz1KadZ1RsAF&branch=master)](https://travis-ci.com/pklejch/GitHub-Issues-Bot)

# GitHub-Issues-Bot
GitHub Issues Bot scans issues of selected repository and tags those issues.

Don't forget to fill auth.conf configuration file. 

## How to test
Run:

*python setup.py test*

or

*pytest -v tests/test_app.py*

If you have filled auth.conf with right values, you can use online testing. With real HTTP requests. Old cassettes will be rewrited. Eg:

*AUTH_FILE=issuelabeler/auth.conf pytest -v tests/test_app.py*

If you dont specify enviroment variable AUTH_FILE, test will use recorded betamax cassettes.
