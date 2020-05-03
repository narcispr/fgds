#!/usr/bin/env python3

from flask import Flask, g, session, render_template, abort, request, flash, redirect, url_for
# from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import datetime

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'frostgrave.db'),
    SECRET_KEY='secret_key',
    USERNAME='admin',
    PASSWORD='1234'
))
app.config.from_envvar('ORGANIZE_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    if error is not None:
        print( "An error has been produced.")


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_members(team):
    db = get_db()
    cur = db.execute("SELECT * FROM minis WHERE team = {}".format(team))
    return cur.fetchall()

def get_stats(id):
    db = get_db()
    cur = db.execute("SELECT * FROM minis WHERE id = {}".format(id))
    return cur.fetchall()

@app.route('/')
def hello():
    minis_1 = get_members(1)
    minis_2 = get_members(2)
    return render_template('select_minis.html', team1=minis_1, team2=minis_2)
    
    
@app.route('/fight/', methods=['POST'])
def fight():
    stats1 = get_stats(request.form['mini1'])
    stats2 = get_stats(request.form['mini2'])
    combat_type = request.form['fight'] == 'combat'
    for i in stats2:
        print(i[1])
    return render_template('fight.html', stats1=stats1, stats2=stats2, combat_type=combat_type)
    

if __name__ == '__main__':
    app.run()
