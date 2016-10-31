import pytest
import betamax
import os
from issuelabeler import issuelabel


with betamax.Betamax.configure() as config:
    if 'AUTH_FILE' in os.environ:
        # If the tests are invoked with an AUTH_FILE environ variable
        TOKEN, _ = issuelabel.readConfig(os.environ['AUTH_FILE'])
        # Always re-record the cassetes
        # https://betamax.readthedocs.io/en/latest/record_modes.html
        config.default_cassette_options['record_mode'] = 'all'
    else:
        TOKEN = 'false_token'
        # Do not attempt to record sessions with bad fake token
        config.default_cassette_options['record_mode'] = 'none'

    # Hide the token in the cassettes
    config.define_cassette_placeholder('<TOKEN>', TOKEN)
    config.cassette_library_dir = 'tests/fixtures/cassettes'



@pytest.fixture
def mySession(betamax_session):
    betamax_session.headers = {'Authorization': 'token ' + TOKEN, 'User-Agent': 'Python'}
    return betamax_session


# return faked parsed rules
@pytest.fixture
def content():
    return ['bug=bug,ff0000','error=bug,ff0000','bot=bot,0000ff',
            '.*=all,ffffff','0x[a-fA-F0-9]+=hexa,00ff00',
            'klejcpet=cool,3e4dd4','@fit.cvut.cz=FIT,238cec',
            '([0-9]{1,3}\.){3}[0-9]{1,3}=ipv4,66cccc']


# test main function labelIssues
@pytest.mark.parametrize('default', ('default', 'vychozi', 'normal'))
@pytest.mark.parametrize('comments', (True, False))
def test_labelIssues(mySession, default, comments):
    issuelabel.labelIssues(mySession, 'MI-PYT-TestRepo', 'pklejchbot', default, comments, 2, content, None)


# test existent labels
@pytest.mark.parametrize('name',('bot','FIT','hexa','ipv4'))
def test_getLabel(mySession, name):
    assert True == issuelabel.getLabel(mySession, 'MI-PYT-TestRepo', 'pklejchbot', name)


# test nonexistent labels
@pytest.mark.parametrize('name',('critical','nonexistentlabel','ipv6'))
def test_getLabel2(mySession, name):
    assert False == issuelabel.getLabel(mySession, 'MI-PYT-TestRepo', 'pklejchbot', name)
