import logging
import dateutil.parser

from flask import Flask, render_template
from flask_ask import Ask, question, statement


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


@ask.intent("DurationIntent")
def log_minutes(duration):
    duration_msg = render_template('run_duration', duration=duration)
    return statement(duration_msg)


@ask.session_ended
def session_ended():
    log.debug("Session ended!")
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
