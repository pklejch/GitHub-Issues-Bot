import configparser
import click
import requests
import re
import time
import os

@click.group()
def cli():
    pass


@cli.command()
def web():
    from .web import app
    app.run(debug=False)

def getDir():
    """
    This function returns directory (as a string) from which is run this tool. It is used as prefix for file path of configuration files.

    :return:

    String with absolute path of directory from which is this tool run.
    """
    return str(os.path.abspath(os.path.dirname(__file__)))

directory = getDir()

@cli.command()
@click.option('--config', '-c', default=directory+"/auth.conf",
              help='Configuration file with authorization tokens.')
@click.option('--repository', '-r', default='MI-PYT-TestRepo',
              help='Target repository which going to be processed.')
@click.option('--rules', '-f', default=directory+'/rules.conf', help='File with rules.')
@click.option('--rate', '-x', default=60,
              help="How long to wait to another run (in seconds).")
@click.option('--default', '-d', default="default",
              help="Default label if none of rules will match.")
@click.option('--comments', '-k', is_flag="True",
              help="Controls if you also search in comments.")
@click.option('--verbose', '-v', count="True", help='Enables verbouse output.')
def console(config, repository, rules, rate, default, comments, verbose):
    """
    Main wrapper function which is run from command line.

    :param string config: Path of the auth configuration file.

    :param string repository: Name of the repository where are issues you want to label.

    :param string rules: Path of the rules configuration file.

    :param int rate: How long to wait to another run (in seconds).

    :param string default: Default label if none of rules will match.

    :param bool comments: Controls if you also search in comments of labels.

    :param int verbose: Enables verbouse output. (0 - no output, 1 - some details, 2 - debug output.)
    """
    if verbose == 2:
        print(os.getcwd() + "\n")
        print("Parsed arguments:")
        print("Config file: " + config + ", repository: " + repository +
              ", file with rules: " + rules + ", rate: " + str(rate) +
              ", default label:" + default + ", process comments flag: "
              + str(comments))
    token, username = readConfig(config)
    session = createSession(token)
    # read all rules
    content = readRules(rules)
    while True:
        if verbose:
            print("Checking issues...")
        labelIssues(session, repository, username,
                    default, comments,
                    verbose, content, None)
        time.sleep(rate)


def readConfig(config):
    """
    This function reads auth configuration file and returns token and username.

    :param string config: Path of the auth configuration file.

    :return:

    Pair of strings with token and username.
    """
    try:
        tokenConfig = configparser.ConfigParser()
        tokenConfig.read(config)
        token = tokenConfig["github"]["token"]
        username = tokenConfig["github"]["username"]
        return token, username
    except KeyError:
        print("Nonexistent or unreadable configuration"
              " file or it is missing directive.")
        exit(1)


def readSecret(config):
    """
    This function reads auth configuration file and returns secret.

    :param string config: Path of the auth configuration file.

    :return:

    String with parsed secret.
    """
    try:
        tokenConfig = configparser.ConfigParser()
        tokenConfig.read(config)
        secret = tokenConfig["github"]["secret"]
        return secret
    except KeyError:
        print("Nonexistent or unreadable configuration"
              " file or it is missing directive.")
        exit(1)


def readRules(rules):
    """
    This function reads rules configuration file.

    :param string rules: Path of the file with rules.

    :return:

    List with lines from configuration file.
    """
    try:
        with open(rules) as f:
            content = f.readlines()
    except EnvironmentError:
        print("Cant read files with rules.")
        exit(1)
    return content


def createSession(token):
    """
    This function creates new session for communicating with GitHub. Session is then used for all functions which communicate with GitHub.

    :param string token: Parsed token from auth configuration file, see :func:`readConfig`.

    :return:

    Created session.
    """

    session = requests.Session()
    session.headers = {'Authorization': 'token ' + token,
                       'User-Agent': 'Python'}
    return session


# get all issues of specified repository
def getIssues(session, repository, username):
    """
    This function fetches all issues from specified repository.

    :param session: Already created session with valid token, see :func:`createSession`.

    :param string repository: Repository which contains issues from which you want to get comments.

    :param string username: Name of the user which owns repository

    :return:

    List of dictionaries with issues.
    """
    query = "https://api.github.com/repos/" \
            + username + "/" + repository + "/issues"
    try:
        r = session.get(query)
        r.raise_for_status()
    except requests.ConnectionError:
        print("Error in communication.")
        exit(1)
    except requests.HTTPError:
        print("Wrong HTTP code. Maybe wrong token, "
              "nonexistent repository, your token doesnt "
              "have access rights, etc.")
        exit(1)
    except requests.Timeout:
        print("Timeouted.")
        exit(1)
    return r.json()


def labelIssues(session, repository, username,
                default, comments, verbose, content, issues):
    """
    Main function of a program.

    :param session: Already created session with valid token, see :func:`createSession`.

    :param string repository: Repository which contains issues you want to label.

    :param string username: Name of the user which owns repository.

    :param string default: Default label if none of rules will match.

    :param bool comments: Controls if comments of issues are searched for match.

    :param int verbose: Verbose level.

    :param list[String] content: List with parsed lines from rules configuration file.

    :param list[Dict] issues: List of dictionaries with issues.

    """
    # launching labelIssues from console, fetch all issues from repository
    if issues is None:
        issues = getIssues(session, repository, username)
    # launching labelIssues from web, add issue to list
    else:
        issuesTmp = list()
        issuesTmp.append(issues)
        issues = issuesTmp

    # for each issue
    for issue in issues:
        # issue doesnt have a label
        if not issue["labels"]:

            # for each rule
            matched = False
            for line in content:

                line = line.strip()
                if line.startswith("#") or line == "":
                    continue

                res = re.match("^\s*([^#]+)\s*=\s*(\w+)\s*"
                               "(,\s*([0-9a-fA-F]{6}))?\s*$", line)
                if not res:
                    continue

                # get rule and label from configuration file
                rule = res.group(1)
                label = res.group(2)

                # if color isnt specified, use default color
                if res.group(4):
                    color = res.group(4)
                else:
                    color = "7a7a7a"

                if verbose == 2:
                    print("PARSED: rule: " + rule + ", label: "
                          + label + ", color: " + color)

                # prepare regex
                pattern = re.compile(rule)

                # test if body (or title) of issue matches regex
                if pattern.search(issue["body"])\
                        or pattern.search(issue["title"]):
                    if verbose == 2:
                        print("Match in " + rule
                              + " and issue #" + str(issue["number"]))
                    matched = True
                    testAndCreateLabel(session, repository,
                                       username, label, color, verbose)
                    addLabel(session, repository, username,
                             label, issue["number"])

                # get comments
                if comments:
                    if verbose:
                        print("Processing comments...")
                    issueComments = getComments(session, repository,
                                                username, issue["number"])
                    for comment in issueComments:
                        if pattern.search(comment["body"]):
                            matched = True
                            if verbose == 2:
                                print("Match in " + rule +
                                      " and comment " + comment["body"])
                            testAndCreateLabel(session, repository, username,
                                               label, color, verbose)
                            addLabel(session, repository, username,
                                     label, issue["number"])

            # if no rule matched this issue, we add default label
            if not matched:
                testAndCreateLabel(session, repository,
                                   username, default, "7a7a7a", verbose)
                addLabel(session, repository,
                         username, default, issue["number"])


def testAndCreateLabel(session, repository, username, label, color, verbose):
    """
    This function tests if specified label exists and if not it will create new label. It uses functions :func:`getLabel` and :func:`createLabel`.

    :param session: Already created session with valid token, see :func:`createSession`.

    :param string repository: Repository where you want to test and create label.

    :param string username: Name of the user which owns repository.

    :param string label: Name of the label you want to test.

    :param string color: Color of label in RGB hex format, without "#" prefix.

    :param int verbose: Verbose level.
    """
    # check if label with this name exists
    if not getLabel(session, repository, username, label):
        # if label doesnt exist, create it
        if verbose == 2:
            print("Creating new label: " + label + ", with color: " + color)
        createLabel(session, repository, username, label, color)
    else:
        if verbose == 2:
            print("Label " + label + " already exists.")


def getLabel(session, repository, username, name):
    """
    This function tests if label exists or not.
    It is used in function :func:`testAndCreateLabel`.

    :param session: Already created session with valid token, see :func:`createSession`.

    :param string repository: Repository which contains label you want to test.

    :param string username: Name of the user which owns repository.

    :param string name: Name of the label you want to test.

    :return:

    True if label exists in repository, False if not.

    """
    query = "https://api.github.com/repos/"\
            + username + "/" + repository + "/labels/" + name
    r = session.get(query)
    if r.status_code == 404:
        return False
    else:
        return True


def getComments(session, repository, username, number):
    """
    This fetches all comments from issue.

    :param session: Already created session with valid token, see :func:`createSession`.

    :param string repository: Repository which contains issue from which you want to get comments.

    :param string username: Name of the user which owns repository.

    :param int number: Number of issue from which you want get comments.

    :return:

    List of dictionaries with comments.
    """
    query = "https://api.github.com/repos/" + \
            username + "/" + repository + \
            "/issues/" + str(number) + "/comments"
    try:
        r = session.get(query)
        r.raise_for_status()
    except requests.ConnectionError:
        print("Error in communication.")
        exit(1)
    except requests.HTTPError:
        print("Wrong HTTP code. Maybe wrong token, "
              "nonexistent repository, your token doesnt "
              "have access rights, etc.")
        exit(1)
    except requests.Timeout:
        print("Timeout.")
        exit(1)
    return r.json()


def createLabel(session, repository, username, label, color):
    """
    This function creates new label.
    It is user responsibility to check if label already exists or not, see :func:`testAndCreateLabel`.

    :param session: Already created session with valid token, see :func:`createSession`.

    :param string repository: Repository where you want to create label.

    :param string username: Name of the user which owns repository.

    :param string label: Name of the label you want to create.

    :param string color: Color of label in RGB hex format, without "#" prefix.

    """
    query = "https://api.github.com/repos/" +\
            username + "/" + repository + "/labels"
    try:
        r = session.post(query,
                         data='{"name": "'+label+'", "color": "'+color+'"}')
        r.raise_for_status()
    except requests.ConnectionError:
        print("Error in communication.")
        exit(1)
    except requests.HTTPError:
        print("Wrong HTTP code. Maybe wrong token, "
              "nonexistent repository, your token doesnt "
              "have access rights, etc.")
        exit(1)
    except requests.Timeout:
        print("Timeout.")
        exit(1)



def addLabel(session, repository, username, label, number):
    """
    This function add existing label to a specified issue.
    It is user responsibility to check if label exists or not, see :func:`testAndCreateLabel`.

    :param session: Already created session with valid token, see :func:`createSession`.

    :param string repository: Repository which contains issue you want to label.

    :param string username: Name of the user which owns repository.

    :param string label: Name of the label you want to add.

    :param int number: Number of issue you want to label.

    """
    query = "https://api.github.com/repos/" +\
            username + "/" + repository + "/issues/" + str(number) + "/labels"
    try:
        r = session.post(query, data='["'+label+'"]')
        r.raise_for_status()
    except requests.ConnectionError:
        print("Error in communication.")
        exit(1)
    except requests.HTTPError:
        print("Wrong HTTP code. Maybe wrong token, "
              "nonexistent repository, your token doesnt "
              "have access rights, etc.")
        exit(1)
    except requests.Timeout:
        print("Timeout.")
        exit(1)


def main():
    """
    Wrapper function for function :func:`cli`.
    This is entry point of this tool.
    """
    cli()
