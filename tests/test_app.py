import pytest
import betamax
import os
import string
import random
import issuelabeler


def createRandomString(size):
    return ''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(size))

with betamax.Betamax.configure() as config:
    if 'AUTH_FILE' in os.environ:
        # If the tests are invoked with an AUTH_FILE environ variable
        TOKEN, username = issuelabeler.issuelabel.readConfig(os.environ['AUTH_FILE'])
        # Always re-record the cassetes
        # https://betamax.readthedocs.io/en/latest/record_modes.html
        config.default_cassette_options['record_mode'] = 'all'
    else:
        TOKEN = 'false_token'
        username = 'noname'
        # Do not attempt to record sessions with bad fake token
        config.default_cassette_options['record_mode'] = 'none'

    # Hide the token in the cassettes
    config.define_cassette_placeholder('<TOKEN>', TOKEN)
    config.define_cassette_placeholder('<USERNAME>', username)
    config.cassette_library_dir = 'tests/fixtures/cassettes'


@pytest.fixture
def mySession(betamax_session):
    betamax_session.headers = {'Authorization': 'token ' + TOKEN,
                               'User-Agent': 'Python'}
    return betamax_session


# return faked parsed rules
@pytest.fixture
def content():
    return ['bug=bug,ff0000', 'error=bug,ff0000', 'bot=bot,0000ff',
            '.*=all,ffffff', '0x[a-fA-F0-9]+=hexa,00ff00',
            'klejcpet=cool,3e4dd4', '@fit.cvut.cz=FIT,238cec',
            '([0-9]{1,3}\.){3}[0-9]{1,3}=ipv4,66cccc']


# test main function labelIssues
@pytest.mark.parametrize('default', ('default', 'vychozi', 'normal'))
@pytest.mark.parametrize('comments', (True, False))
def test_labelIssues(mySession, default, comments):
    issuelabeler.issuelabel.labelIssues(mySession, 'MI-PYT-TestRepo', username,
                                        default, comments, 2, content, None)


# test existent labels
@pytest.mark.parametrize('name', ('bot', 'FIT', 'hexa', 'ipv4'))
def test_getLabel(mySession, name):
    assert True == issuelabeler.issuelabel.getLabel(mySession, 'MI-PYT-TestRepo', username, name)


# test nonexistent labels
@pytest.mark.parametrize('name', ('critical', 'nonexistentlabel', 'ipv6'))
def test_getLabel2(mySession, name):
    assert not issuelabeler.issuelabel.getLabel(mySession, 'MI-PYT-TestRepo', username, name)


# test create label
# i create new unique label and then test if it is available
@pytest.mark.parametrize(('label', 'color'), ((createRandomString(10), '0000ff'),
                                              (createRandomString(10), 'ff0000'),
                                              (createRandomString(10), '00ff00')))
def test_createLabel(mySession, label, color):
    issuelabeler.issuelabel.createLabel(mySession, 'MI-PYT-TestRepo', username, label, color)
    assert True == issuelabeler.issuelabel.getLabel(mySession, 'MI-PYT-TestRepo', username, label)



@pytest.fixture
def testapp():
    from issuelabeler import web
    web.app.config['TESTING'] = True
    return web.app.test_client()


def test_hello(testapp):
    assert 'How to use GitHub Issue Bot' in testapp.get('/').data.decode('utf-8')

