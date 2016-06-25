import logging

from flask import Flask, render_template
from flask_ask import Ask, session, question, statement


app = Flask(__name__)
ask = Ask(app, "/")


log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.launch
def launch():
    return question("How long did your workout take?")


@ask.intent("MinutesIntent")
def log_minutes(minutes):
    log.debug("Logged: " + minutes)
    msg = "OK, {0} minutes.".format(minutes)
    return statement(msg)


@ask.session_ended
def session_ended():
    log.debug("Session ended!")
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
