import logging
import csv
from datetime import datetime, timedelta

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


@ask.intent("DurationIntent", convert={'duration': 'timedelta'})
def log_minutes(duration):
    s = duration.total_seconds()
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    minutes = int(minutes)
    seconds = int(seconds)
    logged_msg = render_template('run_logged',
                                 minutes=minutes,
                                 seconds=seconds)
    personal_best_msg = render_template('personal_best',
                                        minutes=minutes,
                                        seconds=seconds)
    personal_worst_msg = render_template('personal_worst',
                                         minutes=minutes,
                                         seconds=seconds)

    # Parse CSV file and get the personal best/worst.
    get_data = open('data.csv', 'r')
    reader = csv.reader(get_data)
    run_results = (filter(None, sum(list(reader), [])))
    pb = min(run_results)
    pb_ = datetime.strptime(pb, "%H:%M:%S")
    personal_best = timedelta(hours=pb_.hour,
                              minutes=pb_.minute,
                              seconds=pb_.second)
    pw = max(run_results)
    pw_ = datetime.strptime(pw, "%H:%M:%S")
    personal_worst = timedelta(hours=pw_.hour,
                               minutes=pw_.minute,
                               seconds=pw_.second)
    get_data.close()

    # Write duration to CSV file
    write_data = open('data.csv', 'a')
    write_data.write("{0},\n".format(duration))
    write_data.close()

    # Determine what message to play
    if(personal_best > duration):
        return statement(personal_best_msg)
    if(personal_worst < duration):
        return statement(personal_worst_msg)
    else:
        return statement(logged_msg)


@ask.session_ended
def session_ended():
    log.debug("Session ended!")
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
