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
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("MinutesIntent")
def log_minutes(minutes):
    minutes_msg = render_template('run_minutes', minutes=minutes)
    return question(minutes_msg)


@ask.intent("SecondsIntent")
def log_seconds(seconds):
    seconds_msg = render_template('run_seconds', seconds=seconds)
    return statement(seconds_msg)


@ask.session_ended
def session_ended():
    log.debug("Session ended!")
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
